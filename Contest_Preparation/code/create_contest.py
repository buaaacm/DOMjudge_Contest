import argparse
import yaml
import xml.etree.ElementTree as ET
import os
import utils


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add a contest to DOMjudge.')
    parser.add_argument('contest_path', type=str, help='Contest directory (polygon package) path.')
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

    os.chdir(args.contest_path)
    with open('contest.xml', 'r') as fpin:
        root = ET.parse(fpin).getroot()
        problems_node = root.find('problems').findall('problem')

    problems = list()
    for problem in problems_node:
        short_name = problem.attrib['url'].split('/')[-1]
        problems.append(short_name)

    with open('contest.yaml', 'w') as fpout:
        yaml.dump(contest_config, fpout)

    if args.contest_id is None:
        with open('contest.yaml', 'r') as fpin:
            response = utils.post('contests', files={
                'yaml': fpin,
            })
            contest_id = utils.parse_response(response)
    else:
        contest_id = args.contest_id

    os.chdir('domjudge')
    for id, problem in enumerate(problems):
        with open(f'{problem}.zip', 'rb') as fpin:
            problem_index = chr(id + ord('A'))
            response = utils.post(f'contests/{contest_id}/problems', files={
                'zip[]': (f'{problem_index}-{problem}.zip', fpin),
            })
            if response.status_code == 400 and 'externalid' in response.json()['message'][0]:
                print(f'Problem {id} {problem} already exists, ignored...')
            else:
                print(utils.parse_response(response))
