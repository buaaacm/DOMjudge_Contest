import requests
import traceback
from config import *


def get(req_url, params=None):
    return requests.get(f'{url}/api/v4/{req_url}', auth=auth, params=params)


def post(req_url, data=None, files=None):
    return requests.post(f'{req_url}/api/v4/{url}', auth=auth, data=data, files=files)


def parse_response(response):
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        traceback.print_exc()
        print(err)
        print(response.text)
        exit(1)
    return response.json()
