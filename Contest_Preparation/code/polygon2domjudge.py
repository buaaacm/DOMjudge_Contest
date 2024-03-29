import argparse
import shutil
import xml.etree.ElementTree as ET
import os
import yaml
import zipfile
import random
import subprocess
import sys

from config import *


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse Polygon package to DOMjudge format.')
    parser.add_argument('--origin-ml', action='store_true',
                        help='If set, use the original memory limit of Polygon. Otherwise, set memory limit to 2GB.')
    parser.add_argument('--balloon', type=str, help='Balloon color config path. Default: Generate random colors')
    parser.add_argument('--language', type=str, help='Language used in statements Default: chinese', default='chinese')

    args = parser.parse_args()
    shutil.copy(f'../polygon_files/testlib.h', contest_path)
    os.chdir(contest_path)

    if not args.origin_ml:
        print('Warning: Memory limits of all problems are set to 2GB.')

    try:
        shutil.rmtree('domjudge')
    except FileNotFoundError:
        pass

    balloon_config = dict()
    if args.balloon is not None:
        with open(args.balloon, 'r') as fpin:
            balloon_config = yaml.load(fpin, yaml.SafeLoader)

    args.language = args.language.lower()

    with open('contest.xml', 'r') as fpin:
        root = ET.parse(fpin).getroot()
        problems_node = root.find('problems').findall('problem')

    first_problem = True
    for problem in problems_node:
        short_name = problem.attrib['url'].split('/')[-1]
        print(f'Packaging problem {short_name}...')
        with open(f'problems/{short_name}/problem.xml', 'r', encoding='utf-8') as fpin:
            root = ET.parse(fpin).getroot()

        names = root.find('names').findall('name')
        title = None
        for name in names:
            if name.attrib['language'] == args.language:
                title = name.attrib['value']
        escaped_title = title.replace("'", "''")

        testsets = root.find('judging').findall('testset')
        time_limit = int(testsets[0].find('time-limit').text)
        time_limit /= 1000  # ms to s
        memory_limit = int(testsets[0].find('memory-limit').text) if args.origin_ml else (2 << 30)  # 2GB
        memory_limit >>= 20  # in MB
        is_interactive = root.find('assets').find('interactor') is not None
        validation = 'custom interactive' if is_interactive else 'custom'
        problem_config = {
            'validation': validation,  # actually, every problem in Polygon can be treated as special judge
            'limits': {
                'memory': memory_limit,
            },
        }

        workdir = f'domjudge/{short_name}'
        os.makedirs(workdir)
        os.chdir(workdir)

        with open('problem.yaml', 'w') as fpout:
            yaml.dump(problem_config, fpout)

        if short_name in balloon_config:
            color = balloon_config[short_name]
        else:
            color = random.randint(0, (1 << 24) - 1)
            color = f'#{color:06X}'
        problem_config = {
            'name': f"'{escaped_title}'",
            'allow_submit': True,
            'allow_judge': True,
            'timelimit': time_limit,
            'color': color,
        }

        with open('domjudge-problem.ini', 'w') as fpout:
            for key, value in problem_config.items():
                fpout.write(f'{key} = {value}\n')

        for testset in testsets:
            testset_name = testset.attrib['name']
            input_path = testset.find('input-path-pattern').text
            answer_path = testset.find('answer-path-pattern').text
            sample_path = f'data/sample/{testset_name}'
            os.makedirs(sample_path)
            secret_path = f'data/secret/{testset_name}'
            os.makedirs(secret_path)
            tests = testset.find('tests').findall('test')
            for id, test in enumerate(tests):
                if 'sample' in test.attrib:
                    target = sample_path
                else:
                    target = secret_path
                shutil.copy(f'../../problems/{short_name}/{input_path}' % (id + 1), target)
                shutil.copy(f'../../problems/{short_name}/{answer_path}' % (id + 1), target)
            print(r'Warning: removing \r in data, requiring dos2unix...')
            process = subprocess.Popen(r'find data/ -type f -exec dos2unix {} \;',
                                       stdout=sys.stdout, stderr=sys.stderr, shell=True)
            process.communicate()


            def modify_ext(root):
                for rt, dirs, files in os.walk(root):
                    for file in files:
                        base, ext = os.path.splitext(file)
                        if ext == '':
                            shutil.move(os.path.join(root, file), os.path.join(root, f'{base}.in'))
                        elif ext == '.a':
                            shutil.move(os.path.join(root, file), os.path.join(root, f'{base}.ans'))

            modify_ext(sample_path)
            modify_ext(secret_path)

        solutions = root.find('assets').find('solutions').findall('solution')

        tag_map = {  # seems not matched very well ...
            'main': 'accepted',
            'accepted': 'accepted',
            'rejected': 'wrong_answer',
            'wrong-answer': 'wrong_answer',
            'memory-limit-exceeded': 'run_time_error',
            'time-limit-exceeded': 'time_limit_exceeded',
            'time-limit-exceeded-or-accepted': 'time_limit_exceeded',
            'time-limit-exceeded-or-memory-limit-exceeded': 'time_limit_exceeded',
        }
        os.makedirs('submissions/accepted')
        os.makedirs('submissions/wrong_answer')
        os.makedirs('submissions/time_limit_exceeded')
        os.makedirs('submissions/run_time_error')
        for solution in solutions:
            tag = solution.attrib['tag']
            if tag not in tag_map:
                raise NotImplementedError(f'Unknown verdict {tag} on polygon!')
            path = solution.find('source').attrib['path']
            shutil.copy(f'../../problems/{short_name}/{path}', f'submissions/{tag_map[tag]}')

        if is_interactive:
            interactor_path = root.find('assets').find('interactor').find('source').attrib['path']
            dom_interactor_path = 'output_validators'
            os.makedirs(dom_interactor_path)
            shutil.copy(f'../../problems/{short_name}/{interactor_path}', dom_interactor_path)
            shutil.copy(f'../../testlib.h', dom_interactor_path)
        else:
            # DOMjudge will automatically compile those checkers for you! Amazing!
            checker_path = root.find('assets').find('checker').find('source').attrib['path']
            dom_checker_path = 'output_validators'
            os.makedirs(dom_checker_path)
            shutil.copy(f'../../problems/{short_name}/{checker_path}', dom_checker_path)
            shutil.copy(f'../../testlib.h', dom_checker_path)

        if first_problem:
            print('Putting all the statements in the first problem.')
            first_problem = False
            shutil.copy(f'../../statements/{args.language}/statements.pdf', './problem.pdf')

        with zipfile.ZipFile(f'../{short_name}.zip', 'w') as zipf:
            for root, dirs, files in os.walk('.'):
                for file in files:
                    zipf.write(os.path.join(root, file))
        os.chdir('../..')
