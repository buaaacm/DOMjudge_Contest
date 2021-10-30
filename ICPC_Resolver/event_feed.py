import argparse
import json
from datetime import timedelta


def parse_timedelta(string):
    hour, minute, second = string.split(':')
    second, millisecond = second.split('.')
    return timedelta(hours=int(hour), minutes=int(minute), seconds=int(second), milliseconds=int(millisecond))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fix event feed of domjudge.')
    parser.add_argument('available_groups', type=str,
                        help='Available groups, split with comma(,). Example: Participants,Observers')
    parser.add_argument('--award-path', type=str, default='award.json', help='Award file path. Default: award.json.')
    parser.add_argument('--ignore-submission-after', type=str,
                        help='Ignore submission after contest passed this time. Mainly used to ignore too late '
                             'submissions. Format: %%H:%%M:%%S.%%f. Example: 336:00:00.000. Default: contest length.')
    parser.add_argument('--save-path', type=str, default='award-fixed.json',
                        help='Path to save modified event feed. Default: award-fixed.json.')
    args = parser.parse_args()
    events = list()
    with open(args.award_path, 'r') as fpin:
        for line in fpin:
            data = json.loads(line[:-1])
            events.append(data)
    ignore_after = args.ignore_submission_after
    if ignore_after is None:
        for event in events:
            if event['type'] == 'contests':
                ignore_after = event['data']['duration']
    ignore_after = parse_timedelta(ignore_after)

    available_groups = set(args.available_groups.split(','))
    ignore_groups = set()
    for event in events:
        if event['type'] == 'groups':
            if event['data']['name'] not in available_groups:
                ignore_groups.add(event['data']['id'])
    ignore_teams = set()
    for event in events:
        if event['op'] == 'delete':
            continue
        if event['type'] == 'teams':
            ignore = False
            for group_id in event['data']['group_ids']:
                if group_id in ignore_groups:
                    ignore = True
                    break
            if ignore:
                ignore_teams.add(event['data']['id'])

    ignore_submissions = set()
    for event in events:
        if event['type'] == 'submissions':
            ignore = False
            if event['data']['team_id'] in ignore_teams:
                ignore = True
            else:
                time_passed = event['data']['contest_time']
                if time_passed.startswith('-'):
                    raise RuntimeError('Negative time found, possibly admin solution, did you ignore admin group?')
                time_passed = parse_timedelta(time_passed)
                if time_passed > ignore_after:
                    ignore = True
            if ignore:
                sid = event['data']['id']
                ignore_submissions.add(sid)
                print(f'Ignore submission {sid}')
    ignore_judgements = set()
    for event in events:
        if event['type'] == 'judgements':
            if event['data']['submission_id'] in ignore_submissions:
                ignore_judgements.add(event['data']['id'])
    ignore_runs = set()
    for event in events:
        if event['type'] == 'runs':
            if event['data']['judgement_id'] in ignore_judgements:
                ignore_runs.add(event['data']['id'])
    fixed_events = list()
    for event in events:
        if event['op'] == 'delete':
            pass
        elif event['type'] == 'groups' and event['data']['id'] in ignore_groups:
            continue
        elif event['type'] == 'teams' and event['data']['id'] in ignore_teams:
            continue
        elif event['type'] == 'submissions' and event['data']['id'] in ignore_submissions:
            continue
        elif event['type'] == 'judgements' and event['data']['id'] in ignore_judgements:
            continue
        elif event['type'] == 'runs' and event['data']['id'] in ignore_runs:
            continue
        fixed_events.append(event)
    with open(args.save_path, 'w') as fpout:
        for event in fixed_events:
            fpout.write(json.dumps(event) + '}\n')
