from requests.auth import HTTPBasicAuth


url = 'http://localhost:12345/'
username = 'admin'
password = 'password'
auth = HTTPBasicAuth(username, password)
