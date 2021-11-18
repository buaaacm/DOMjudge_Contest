import re
import argparse
import xml.etree.ElementTree as ET
import utils
import os


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
    response = utils.get(f'contests/{contest_id}/problems')
    problems = utils.parse_response(response)
    config = list()
    for problem in problems:
        pid = problem['id']
        response = utils.get(f'contests/{contest_id}/problems/{pid}')
        problem_info = utils.parse_response(response)
        short_name = problem_info['short_name']
        tl = problem['time_limit']
        print(f'{short_name}, {tl} seconds')
        config.append((tl, 1 << 11))  # DOMjudge 居然不返回 ML...
    return config


def get_config(args):
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
    parser.add_argument('op', type=str, choices=['get', 'set'], help='Get or set.')
    parser.add_argument('contest_path', type=str, help='Contest directory (polygon package) path.')
    parser.add_argument('contest_id', type=str, help='DOMjudge contest id.')

    args = parser.parse_args()
    os.chdir(args.contest_path)
    if args.op == 'get':
        get_config(args)
    elif args.op == 'set':
        set_config(args)
