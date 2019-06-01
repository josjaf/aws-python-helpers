import logging

from stacker.lookups.handlers.output import OutputLookup
from stacker.lookups.handlers.rxref import RxrefLookup
from stacker.lookups.handlers.xref import XrefLookup
from stacker.session_cache import get_session



from botocore.exceptions import ClientError
from newport_helpers import helpers, cfn_helpers, docker_helpers


import boto3
import docker
import datetime
import git
from base64 import b64decode
from newport_helpers.super import super

s = super.Super()

LOGGER = logging.getLogger(__name__)




def handler(context, provider, **kwargs):
    session = get_session(provider.region)
    handler = OutputLookup.handle
    value = kwargs['ecrid']
    stack_name = context.get_fqn(value.split('::')[0])
    docker_file = kwargs['dockerfile']
    tag = kwargs['docker_tag']
    print(f"Looking up ECR ID from {stack_name}")
    try:  # Exit early if the bucket's stack is already deleted
        session.client('cloudformation').describe_stacks(
            StackName=context.get_fqn(value.split('::')[0])
        )

    except ClientError as exc:
        if 'does not exist' in exc.response['Error']['Message']:
            LOGGER.info('S3 bucket stack appears to have already been '
                        'deleted...')
            return True
        raise
    ecr_name = handler(
        value,
        provider=provider,
        context=context
    )
    repo = git.Repo(search_parent_directories=True)
    sha = repo.head.object.hexsha
    t = datetime.datetime.now()
    buildtime = t.strftime("%m-%d-%Y %H:%M:%S")

    labels = {'Maintainer': 'josjaf', 'commit': sha, 'buildtime': buildtime}
    s.Docker_Helpers.docker_build_image(tag, docker_file, labels)



    session = boto3.session.Session()
    region = session.region_name
    identity = session.client("sts").get_caller_identity()
    account_id = identity["Account"]
    registry = f"{account_id}.dkr.ecr.{region}.amazonaws.com/{ecr_name}"

    # tag image
    docker_client = docker.from_env()
    image = docker_client.images.get(f'{tag}:latest')
    image.tag(registry, 'latest')


    # login
    ecr = session.client('ecr', region_name=session.region_name)
    login_response = ecr.get_authorization_token()
    token = b64decode(login_response['authorizationData'][0]['authorizationToken']).decode()
    username, password = token.split(':', 1)
    print(username, password)
    print(f"UserName: {username}")
    print(f"Password: {password}")
    response = docker_client.login(username=username, password=password, registry=registry, reauth=True, email=None)
    print(response)
    response = docker_client.images.push(registry, tag="latest", auth_config=dict(username=username, password=password))
    print(response)
    return labels


if __name__ == '__main__':
    handler(context, provider, **kwargs)
