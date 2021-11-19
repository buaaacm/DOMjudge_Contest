from requests.auth import HTTPBasicAuth
import yaml

with open('config.yaml', 'r') as fpin:
    config = yaml.load(fpin, yaml.SafeLoader)

url = config['url']
username = config['username']
password = config['password']
auth = HTTPBasicAuth(username, password)
contest_path = config['contest_path']

locust_statement_id = config['locust']['statement_id']
locust_contest_id = config['locust']['contest_id']
locust_submit_prob = config['locust']['submit_prob']
