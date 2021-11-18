import argparse
import random
import utils


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate teams, users, and add them to DOMjudge.')
    parser.add_argument('team', type=int, help='Team number')
    parser.add_argument('group_id', type=int, help='Group id')
    parser.add_argument('--pwd-len', type=int, default=12, help='Password length')
    args = parser.parse_args()


    with open('teams2.tsv', 'w') as fpout:
        fpout.write('File_Version\t2\n')
        for i in range(args.team):
            team_id = 10 + i  # The 10 is tricky. You should make them unique (different with existed accounts, such as admin), and be the same as team_name.
            external_id = team_id
            category_id = [args.group_id]
            team_name = f'team{team_id:03d}'
            institution_name = '北京航空航天大学'
            institution_short_name = 'BUAA'
            country_code = 'CHN'
            external_institution_id = 'You said it can be empty???'  # dummy
            fpout.write('\t'.join([str(team_id), str(external_id), str(category_id), team_name, institution_name,
                                   institution_short_name, country_code, external_institution_id]) + '\n')

    with open('teams2.tsv', 'r') as fpin:
        response = utils.post('users/teams', files={
            'tsv': fpin,
        })
        print(response.json())
        response.raise_for_status()

    with open('accounts.tsv', 'w') as fpout:
        fpout.write('accounts\t1\n')
        for i in range(args.team):
            user_type = 'team'
            full_name = f'team{10 + i:03d}'
            username = full_name
            ban_char = '0129IOQZ'  # Ban confusing characters
            charset = [chr(j) for j in range(ord('A'), ord('Z') + 1)] + \
                      [chr(j) for j in range(ord('a'), ord('z') + 1)] + \
                      [chr(j) for j in range(ord('0'), ord('9') + 1)]
            charset = [ch for ch in charset if ch not in ban_char]
            password = ''
            for j in range(args.pwd_len):
                password += charset[random.randint(0, len(charset) - 1)]
            fpout.write('\t'.join([user_type, full_name, username, password]) + '\n')

    with open('accounts.tsv', 'r') as fpin:
        response = utils.post('users/accounts', files={
            'tsv': fpin,
        })
        print(response.json())
        response.raise_for_status()
