import argparse
import requests
from requests.auth import HTTPBasicAuth
import yaml
import xml.etree.ElementTree as ET
import os


def post(url, data=None, files=None):
    global args
    return requests.post(f'{args.url}/api/v4/{url}', auth=HTTPBasicAuth('admin', 'ioSLpaVyuIF-MsPy'), data=data, files=files)


def parse_response(response):
    try:
        print(response.json())
    except:
        print(response.text)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add a contest to DOMjudge.')
    parser.add_argument('url', type=str, help='DOMjudge url. Example: https://bcpc.buaaacm.com/domjudge')
    parser.add_argument('--contest', type=str, default='contest.yaml', help='Contest config path. Default: contest.yaml')
    args = parser.parse_args()

    with open(args.contest, 'r') as fpin:
        contest_config = yaml.load(fpin, yaml.SafeLoader)
    with open('contest.xml', 'r') as fpin:
        root = ET.parse(fpin).getroot()
        problems_node = root.find('problems').findall('problem')

    problems = list()
    for problem in problems_node:
        short_name = problem.attrib['url'].split('/')[-1]
        problems.append(short_name)

    with open(args.contest, 'w') as fpout:
        yaml.dump(contest_config, fpout)

    with open(args.contest, 'r') as fpin:
        response = post('contests', files={
            'yaml': fpin,
        })
        parse_response(response)
        response.raise_for_status()
        contest_id = response.json()

    os.chdir('domjudge')
    for id, problem in enumerate(problems):
        with open(f'{problem}.zip', 'rb') as fpin:
            if id == len(problems) - 1:
                problem_index = 'Z'
            else:
                problem_index = chr(id + ord('A'))
            response = post(f'contests/{contest_id}/problems', files={
                'zip[]': (f'{problem_index}.zip', fpin),
            })
            parse_response(response)
            response.raise_for_status()
