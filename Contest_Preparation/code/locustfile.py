from bs4 import BeautifulSoup
from locust import HttpUser, task, between
import random
import csv
import xml.etree.ElementTree as ET
import os
from datetime import datetime, timedelta
import subprocess
import sys
import shutil

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
    def get_with_resources(self, page):
        if page not in self.wget_last_update or datetime.now() - self.wget_last_update[page] > timedelta(minutes=10):
            print(f'Wgetting for user {self.username}, page {page}')
            workdir = f'/tmp/domjudge/{self.username}'
            shutil.rmtree(workdir, ignore_errors=True)
            os.makedirs(workdir)

            cookies = self.client.cookies.get_dict()
            cookie_file = os.path.join(workdir, 'cookies.txt')
            with open(cookie_file, 'w') as fpout:
                for key, value in cookies.items():
                    cookie = [self.domain, 'TRUE', '/', 'FALSE', '10000000000', key, value]
                    fpout.write('\t'.join(cookie) + '\n')
            process = subprocess.Popen(f'wget -P {workdir} -p {self.client.base_url}{page} '
                                       f'--load-cookies {cookie_file}',
                                       stdout=sys.stdout, stderr=sys.stderr, shell=True)
            process.communicate()
            all_resources = list()
            resouce_path = os.path.join(workdir, self.domain)
            for root, dirs, files in os.walk(resouce_path):
                for file in files:
                    if file == 'robots.txt':
                        continue
                    all_resources.append('/' + os.path.relpath(os.path.join(root, file), resouce_path))
            print(f'Resouces, current time {datetime.now()}:')
            for resource in all_resources:
                print(resource)
            self.all_resources[page] = all_resources
            self.wget_last_update[page] = datetime.now()
        for resource in self.all_resources[page]:
            self.client.get(resource)

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
        self.username = username
        self.wget_last_update = dict()
        self.all_resources = dict()
        domain = self.client.base_url.strip('/')
        for protocol in ['http', 'https']:
            if domain.startswith(f'{protocol}://'):
                domain = domain[len(f'{protocol}://'):]
        self.domain = domain
