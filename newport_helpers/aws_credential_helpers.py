import boto3
from . import log_helpers
logger = log_helpers.get_logger()

def get_credentials(session=boto3.session.Session()):
    """
    get credentials dictionary from boto3, can be used to pass into docker container not running on aws
    useful for local testing of docker
    :return:
    """
    credentials = {}
    credentials['AWS_ACCESS_KEY_ID'] = session.get_credentials().access_key
    credentials['AWS_SECRET_ACCESS_KEY'] = session.get_credentials().secret_key
    credentials['AWS_SESSION_TOKEN'] = session.get_credentials().token
    credentials['AWS_DEFAULT_REGION'] = session.region_name
    return credentials
