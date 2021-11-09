import re
import argparse
import xml.etree.ElementTree as ET
import requests
import traceback
from requests.auth import HTTPBasicAuth


domjudge_url = ''
auth = HTTPBasicAuth('admin', 'password')


def get(url, params=None):
    return requests.get(f'{domjudge_url}/api/v4/{url}', auth=auth, params=params)


def post(url, data=None, files=None):
    return requests.post(f'{domjudge_url}/api/v4/{url}', auth=auth, data=data, files=files)


def parse_response(response):
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        traceback.print_exc()
        print(err)
        print(response.text)
        exit(1)
    return response.json()


def parse_statement():
    with open('contest.xml', 'r') as fpin:
        root = ET.parse(fpin).getroot()
        problems_node = root.find('problems').findall('problem')
        language = root.find('names').find('name').attrib['language']
    file_list = list()
    for problem in problems_node:
        short_name = problem.attrib['url'].split('/')[-1]
        file_list.append((short_name, f'problems/{short_name}/statements/{language}/problem.tex'))
    return file_list


def parse_domjudge(contest_id):
    response = get(f'contests/{contest_id}/problems')
    problems = parse_response(response)
    config = list()
    for problem in problems:
        pid = problem['id']
        response = get(f'contests/{contest_id}/problems/{pid}')
        problem_info = parse_response(response)
        short_name = problem_info['short_name']
        tl = problem['time_limit']
        print(f'{short_name}, {tl} seconds')
        config.append((tl, 1 << 11))  # DOMjudge 居然不返回 ML...
    return config


def get_config(args):
    global domjudge_url
    domjudge_url = args.url
    file_list = parse_statement()
    for index, (short_name, file) in enumerate(file_list):
        with open(file, 'r', encoding='utf-8') as fpin:
            lines = fpin.readlines()
            parts = [part for part in re.split('[{}]', lines[0]) if part]
            index = chr(index + ord('A'))
            print(f'{index}, {parts[5]}, {parts[6]}, {short_name}')
    print()
    parse_domjudge(args.contest_id)


def set_config(args):
    global domjudge_url
    domjudge_url = args.url
    config = parse_domjudge(args.contest_id)
    file_list = parse_statement()
    for index, (_, file) in enumerate(file_list):
        with open(file, 'r', encoding='utf-8') as fpin:
            lines = fpin.readlines()

        tl = str(config[index][0])
        if '.' in tl:
            if int(tl.split('.')[1]) == 0:
                tl = tl.split('.')[0]
            else:
                tl = tl.strip('0')
        if tl == '1':
            tl += ' second'
        else:
            tl += ' seconds'

        ml = f'{config[index][1]} megabytes'

        parts = [part for part in re.split('[{}]', lines[0]) if part]
        parts[5] = tl
        parts[6] = ml
        for i in range(1, 7):
            parts[i] = f'{{{parts[i]}}}'
        lines[0] = ''.join(parts)

        with open(file, 'w', encoding='utf-8') as fpout:
            fpout.writelines(lines)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compare the time limit and the memory limit of the statement and the'
                                                 ' domjudge setting.')
    subparsers = parser.add_subparsers(title='subcommands', description='valid subcommands', help='additional help')

    parser_get = subparsers.add_parser('get', description='Get the time limit and the memory limit of the statement and'
                                                          ' the domjudge setting.')
    parser_get.add_argument('url', type=str, help='DOMjudge url. Example: https://pre.bcpc.buaaacm.com/')
    parser_get.add_argument('contest_id', type=str, help='DOMjudge contest id.')
    parser_get.set_defaults(func=get_config)

    parser_set = subparsers.add_parser('set', description='Set the time limit and the memory limit of the statement to'
                                                          ' the domjudge setting.')
    parser_set.add_argument('url', type=str, help='DOMjudge url. Example: https://pre.bcpc.buaaacm.com/')
    parser_set.add_argument('contest_id', type=str, help='DOMjudge contest id.')
    parser_set.set_defaults(func=set_config)

    args = parser.parse_args()
    args.func(args)
