import argparse
import requests
from requests.auth import HTTPBasicAuth
import random
import time
import os
import xml.etree.ElementTree as ET


authentication = HTTPBasicAuth('admin', 'password')


def get(url, auth=authentication, params=None):
    global args
    return requests.get(f'{args.url}/api/v4/{url}', auth=auth, params=params)


def post(url, auth=authentication, data=None, files=None):
    global args
    return requests.post(f'{args.url}/api/v4/{url}', auth=auth, data=data, files=files)


def parse_response(response):
    try:
        print(response.json())
    except:
        print(response.text)
    response.raise_for_status()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Randomly submit to DOMjudge.')
    parser.add_argument('url', type=str, help='DOMjudge url. Example: https://bcpc.buaaacm.com/domjudge')
    parser.add_argument('contest_id', type=int, help='Contest Id')
    parser.add_argument('--submit-interval', type=int, default=10, help='Interval between submissions')
    args = parser.parse_args()

    teams = list()
    with open('../accounts.tsv', 'r') as fpin:
        for line in fpin:
            line = line.strip().split('\t')
            if line[0] == 'accounts':
                continue
            teams.append((line[1], line[3]))

    with open('contest.xml', 'r') as fpin:
        root = ET.parse(fpin).getroot()
        problems_node = root.find('problems').findall('problem')
        problems = list()
        for problem in problems_node:
            problems.append(problem.attrib['url'].split('/')[-1])

    domjudge_problems = get(f'contests/{args.contest_id}/problems').json()
    problems_id = [p['id'] for p in domjudge_problems]
    print(problems_id)

    while True:
        problem = random.randint(0, len(problems) - 1)
        short_name = problems[problem]
        codes = list()
        for root, dirs, files in os.walk(f'domjudge/{short_name}/submissions'):
            for file in files:
                codes.append(os.path.join(root, file))
        code = codes[random.randint(0, len(codes) - 1)]
        ext = os.path.splitext(code)[-1]
        language = {
            '.cc': 'cpp',
            '.cpp': 'cpp',
            '.py': 'python3',
            '.java': 'java',
        }[ext]
        team = teams[random.randint(0, len(teams) - 1)]
        with open(code, 'r') as fpin:
            response = post(f'contests/{args.contest_id}/submissions', auth=HTTPBasicAuth(team[0], team[1]), data={
                'problem': problems_id[problem],
                'language': language,
            }, files={
                'code[]': fpin,
            })
            print(response.json())
            response.raise_for_status()
        time.sleep(args.submit_interval)
