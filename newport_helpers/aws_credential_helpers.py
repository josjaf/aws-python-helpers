import boto3
import newport_helpers
logger = newport_helpers.nph.logger

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
