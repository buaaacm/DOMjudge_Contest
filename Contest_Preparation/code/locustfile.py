from bs4 import BeautifulSoup
from locust import HttpUser, task, between
import random
import csv
import xml.etree.ElementTree as ET
import os

from config import *
import utils

students = list()
with open('../output/participant_info.csv', 'r') as fpin:
    info = list(csv.reader(fpin))[1:]
    for student in info:
        students.append((student[2], student[3]))
random.shuffle(students)

response = utils.get(f'contests/{locust_contest_id}/problems')
domjudge_problems = utils.parse_response(response)
problems_id = [p['id'] for p in domjudge_problems]
with open(os.path.join(contest_path, 'contest.xml'), 'r') as fpin:
    root = ET.parse(fpin).getroot()
codes = list()
problems_node = root.find('problems').findall('problem')
for problem in problems_node:
    short_name = problem.attrib['url'].split('/')[-1]
    code = list()
    for root, dirs, files in os.walk(os.path.join(contest_path, f'domjudge/{short_name}/submissions')):
        for file in files:
            with open(os.path.join(root, file)) as fpin:
                ext = os.path.splitext(file)[-1]
                language = {
                    '.c': 'c',
                    '.cc': 'cpp',
                    '.cpp': 'cpp',
                    '.c++': 'cpp',
                    '.cxx': 'cpp',
                    '.py': 'py3',
                    '.py3': 'py3',
                    '.java': 'java',
                }[ext]
                code.append({
                    'filename': file,
                    'language': language,
                    'content': fpin.read(),
                })
    codes.append(code)


class QuickstartUser(HttpUser):
    wait_time = between(10, 15)

    # TODO: 这份测试只下载了 HTML 页面本身，没有下载相关的 JS/CSS/IMG 等。如果之后要实现相关功能的话，可参考 wget 源码

    @task
    def home(self):
        self.client.get('/team')

    @task
    def problems(self):
        self.client.get('/team/problems')

    @task
    def problem_text(self):
        self.client.get(f'/team/problems/{locust_statement_id}/text')

    @task
    def submit(self):
        if random.randint(0, locust_submit_prob - 1) > 0:
            return
        with self.client.get('/team/submit', catch_response=True) as response:
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_token = soup.find(attrs={'name': 'submit_problem[_token]'}).attrs['value']
        index = random.randint(0, len(problems_id) - 1)
        code = random.choice(codes[index])
        self.client.post(
            f'/team/submit',
            data={
                'submit_problem[problem]': problems_id[index],
                'submit_problem[language]': code['language'],
                'submit_problem[_token]': csrf_token,
                'submit_problem[entry_point]': '',
            },
            files={
                'submit_problem[code][]': (code['filename'], code['content'], 'application/octet-stream'),
            }
        )
        self.client.get('/team')

    @task
    def clarification(self):
        if random.randint(0, locust_clarification_prob - 1) > 0:
            return
        with self.client.get('/team/clarifications/add', catch_response=True) as response:
            soup = BeautifulSoup(response.text, 'html.parser')
            recipients = soup.find(attrs={'name': 'team_clarification[recipient]'}).find_all('option')
            recipient = random.choice(recipients).attrs['value']
            subjects = soup.find(attrs={'name': 'team_clarification[subject]'}).find_all('option')
            subject = random.choice(subjects).attrs['value']
            csrf_token = soup.find(attrs={'name': 'team_clarification[_token]'}).attrs['value']
        self.client.post(
            f'/team/clarifications/add',
            data={
                'team_clarification[recipient]': recipient,
                'team_clarification[subject]': subject,
                'team_clarification[message]':
                    ''.join([random.choice('01') for _ in range(locust_clarification_length)]),
                'team_clarification[_token]': csrf_token,
            }
        )
        self.client.get('/team')

    @task
    def scoreboard(self):
        self.client.get('/team/scoreboard')

    def on_start(self):
        with self.client.get('/login', catch_response=True) as response:
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_token = soup.find(attrs={'name': '_csrf_token'}).attrs['value']
        username, password = students.pop()
        print(f'{username} login')
        self.client.post(
            '/login',
            data={'_username': username, '_password': password, '_csrf_token': csrf_token}
        )
