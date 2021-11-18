import argparse
import random
import utils
import csv
import json


def gen_password(length):
    ban_char = '01269CIKOPQSUVWXZbcgiklopsuvwxz'  # Ban confusing characters
    charset = [chr(j) for j in range(ord('A'), ord('Z') + 1)] + \
              [chr(j) for j in range(ord('a'), ord('z') + 1)] + \
              [chr(j) for j in range(ord('0'), ord('9') + 1)]
    charset = [ch for ch in charset if ch not in ban_char]
    password = ''
    for j in range(length):
        password += charset[random.randint(0, len(charset) - 1)]
    return password


if __name__ == '__main__':
    gen_password(0)
    parser = argparse.ArgumentParser(description='Generate teams, users, and add them to DOMjudge.')
    parser.add_argument('group_id', type=int, help='Group id to register teams.')
    parser.add_argument(
        'max_team_id',
        type=int,
        help='Maximum team id that currently exists. You should manually '
             'check it from DOMjudge/database to avoid duplication.'
    )
    parser.add_argument(
        '--team-csv',
        type=str,
        default='../input/team_info.csv',
        help='Team csv file path. Default: ../input/team_info.csv. Refer to the sample file to check its format.'
    )
    parser.add_argument(
        '--seats',
        type=str,
        default='../input/seats.txt',
        help='Location file path. Default: ../input/seats.txt. File that lists all available seats.'
    )
    parser.add_argument('--pwd-len', type=int, default=12, help='Password length. Default: 12.')
    args = parser.parse_args()

    with open(args.seats, 'r', encoding='utf-8') as fpin:
        seats = list()
        for line in fpin:
            line = line.strip()
            if line:
                seats.append(line)
        random.shuffle(seats)

    max_team_id = args.max_team_id
    teams = list()
    accounts = [['accounts', '1']]
    participant_info = [[
        '学号',
        '姓名',
        '用户名',
        '密码',
        '座位',
    ]]
    with open(args.team_csv, 'r', encoding='utf-8') as fpin:
        for index, team in enumerate(csv.reader(fpin)):
            team_name = f'{team[0]}-{team[1]}'
            team_id = max_team_id + 1 + index
            seat = seats[index]
            teams.append({
                'id': team_id,
                'group_ids': [args.group_id],
                'name': team_name,
                'display_name': team_name,
                'organization_id': 'BUAA',
                'location': seat,
            })

            password = gen_password(args.pwd_len)
            username = f'team{team_id:04d}'  # Team id should be a prefix of username
            accounts.append([
                'team',
                team[1],  # Full name
                username,
                password,
            ])

            participant_info.append([
                team[0],  # Student number
                team[1],  # Full name
                username,
                password,
                seat,
            ])

    with open('../output/teams.json', 'w', encoding='utf-8') as fpout:
        json.dump(teams, fpout)

    with open('../output/accounts.tsv', 'w', encoding='utf-8') as fpout:
        csv.register_dialect('tsv_dialect', delimiter='\t')
        writer = csv.writer(fpout, dialect='tsv_dialect')
        writer.writerows(accounts)

    with open('../output/participant_info.csv', 'w', encoding='csv') as fpout:
        writer = csv.writer(fpout)
        writer.writerows(participant_info)

    with open('../output/teams.json', 'r') as fpin:
        response = utils.post('users/teams', files={
            'json': fpin,
        })
        print(utils.parse_response(response))
    with open('../output/accounts.tsv', 'r') as fpin:
        response = utils.post('users/accounts', files={
            'tsv': fpin,
        })
        print(utils.parse_response(response))
