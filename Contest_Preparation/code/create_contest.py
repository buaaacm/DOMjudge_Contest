import argparse
import yaml
import xml.etree.ElementTree as ET
import os
import utils
from config import *


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add a contest to DOMjudge.')
    parser.add_argument(
        '--contest',
        type=str,
        default='../input/contest.yaml',
        help='Contest config path. Default: ../input/contest.yaml'
    )
    parser.add_argument('--contest-id', type=int, help='Contest id if the contest exists.')
    args = parser.parse_args()

    with open(args.contest, 'r') as fpin:
        contest_config = yaml.load(fpin, yaml.SafeLoader)

    os.chdir(contest_path)
    with open('contest.xml', 'r') as fpin:
        root = ET.parse(fpin).getroot()
        problems_node = root.find('problems').findall('problem')

    problems = list()
    for problem in problems_node:
        short_name = problem.attrib['url'].split('/')[-1]
        problems.append(short_name)

    if args.contest_id is None:
        response = utils.post('contests', files={
            'yaml': ('contest.yaml', yaml.dump(contest_config)),
        })
        contest_id = utils.parse_response(response)
        exist_problems = set()
    else:
        contest_id = args.contest_id
        response = utils.get(f'contests/{contest_id}/problems')
        exist_problems = utils.parse_response(response)
        exist_problems = {problem['externalid'] for problem in exist_problems}

    os.chdir('domjudge')
    for id, problem in enumerate(problems):
        with open(f'{problem}.zip', 'rb') as fpin:
            problem_index = chr(id + ord('A'))
            name = f'{problem_index}-{problem}'
            # if response.status_code == 400 and 'externalid' in response.json()['message']:
            #     print(f'Problem {id} {problem} already exists, ignored...')
            if name in exist_problems:
                print(f'Problem {id} {problem} already exists, ignored...')
                continue
            else:
                response = utils.post(f'contests/{contest_id}/problems', files={
                    'zip[]': (f'{name}.zip', fpin),
                })
                print(utils.parse_response(response))
