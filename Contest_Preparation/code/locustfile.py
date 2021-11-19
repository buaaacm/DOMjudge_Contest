from bs4 import BeautifulSoup
from locust import HttpUser, task, between
import random
import csv


### Fill the following configuration before you start testing

# The problem with statement, usually problem A
statement_id = 5

### Configuration end

students = list()
with open('../output/participant_info.csv', 'r') as fpin:
    info = list(csv.reader(fpin))[1:]
    for student in info:
        students.append((student[2], student[3]))
random.shuffle(students)


class QuickstartUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def home(self):
        self.client.get('/team')

    @task
    def problems(self):
        self.client.get('/team/problems')

    @task
    def problem_text(self):
        self.client.get(f'/team/problems/{statement_id}/text')

    def on_start(self):
        response = self.client.get('/login')
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token = soup.find(attrs={'name': '_csrf_token'}).attrs['value']
        username, password = students.pop()
        print(f'{username} login')
        self.client.post(
            '/login',
            data={'_username': username, '_password': password, '_csrf_token': csrf_token}
        )
