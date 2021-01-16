import boto3


def get_credentials():
    """
    get credentials dictionary from boto3, can be used to pass into docker container not running onaws
    :return:
    """
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
