import boto3
from newport_helpers import helpers
import botocore
import uuid
import datetime
import time


class AWSCredentialHelpers():
    def __init__(self, *args, **kwargs):
        return

    def get_credentials(self):
        credentials = {}
        available_profiles = boto3.session.Session().available_profiles

        if 'example' in available_profiles:
            print("using example profile")
            session = boto3.session.Session(profile='example')
        else:
            session = boto3.session.Session()

        credentials['AWS_ACCESS_KEY_ID'] = session.get_credentials().access_key
        credentials['AWS_SECRET_ACCESS_KEY'] = session.get_credentials().secret_key
        credentials['AWS_SESSION_TOKEN'] = session.get_credentials().token
        credentials['AWS_DEFAULT_REGION'] = session.region_name
        return credentials