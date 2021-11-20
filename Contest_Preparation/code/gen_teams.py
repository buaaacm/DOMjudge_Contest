import argparse
import random
import utils
import csv
import json
import io


def gen_password(length):
    ban_char = '01269CIKOPQSUVWXZbcgiklopsuvwxz'  # Ban confusing characters
    charset = [chr(j) for j in range(ord('A'), ord('Z') + 1)] + \
              [chr(j) for j in range(ord('a'), ord('z') + 1)] + \
              [chr(j) for j in range(ord('0'), ord('9') + 1)]
    charset = [ch for ch in charset if ch not in ban_char]
    password = ''
    for j in range(length):
        password += random.choice(charset)
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
    participant_header = [
        '学号',
        '姓名',
        '用户名',
        '密码',
        '座位',
        'Team ID',
        '队伍名',
    ]
    participant_info = list()
    with open(args.team_csv, 'r', encoding='utf-8') as fpin:
        for index, team in enumerate(csv.reader(fpin)):
            team_name = f'{team[0]}-{team[1]}'
            team_id = max_team_id + 1 + index
            seat = seats[index]

            password = gen_password(args.pwd_len)
            username = f'team{team_id:04d}'  # Team id should be a prefix of username

            participant_info.append({
                '学号': team[0],
                '姓名': team[1],
                '用户名': username,
                '密码': password,
                '座位': seat,
                'Team ID': team_id,
                '队伍名': team_name,
            })
    with open('../output/participant_info.csv', 'w', encoding='utf-8') as fpout:
        writer = csv.DictWriter(fpout, participant_header)
        writer.writeheader()
        writer.writerows(participant_info)

    SLICE = 50
    while participant_info:
        if len(participant_info) < 50:
            to_process = participant_info
            participant_info = []
        else:
            to_process = participant_info[-50:]
            assert len(to_process) == 50
            del participant_info[-50:]
        teams = list()
        accounts = [['accounts', '1']]
        for participant in to_process:
            teams.append({
                'id': participant['Team ID'],
                'group_ids': [args.group_id],
                'name': participant['队伍名'],
                'display_name': participant['队伍名'],
                'organization_id': 'BUAA',
                'location': participant['座位'],
            })

            accounts.append([
                'team',
                participant['姓名'],
                participant['用户名'],
                participant['密码'],
            ])

        response = utils.post('users/teams', files={
            'json': ('teams.json', json.dumps(teams))
        })
        print(utils.parse_response(response))

        str_out = io.StringIO()
        csv.register_dialect('tsv_dialect', delimiter='\t')
        writer = csv.writer(str_out, dialect='tsv_dialect')
        writer.writerows(accounts)
        response = utils.post('users/accounts', files={
            'tsv': ('accounts.tsv', str_out.getvalue()),
        })
        print(utils.parse_response(response))
