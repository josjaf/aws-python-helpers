"""
post_build:
  push_image:
    path: stacker_custom.hooks.post.docker_build_push.handler
    required: true
    args:
      ecrid: ecr::ecrid
      dockerfile: Dockerfile
      path: app_pipeline
      docker_tag: ${docker_stack_set_tag}

"""
import logging

from stacker.lookups.handlers.output import OutputLookup
from stacker.lookups.handlers.rxref import RxrefLookup
from stacker.lookups.handlers.xref import XrefLookup
from stacker.session_cache import get_session
from stacker.logger import setup_logging
from botocore.exceptions import ClientError

import boto3
import docker
import datetime
import git
from base64 import b64decode
import newport_helpers
from newport_helpers import NPH

NPH = NPH.NPH()

logger = logging.getLogger(__name__)


def handler(context, provider, **kwargs):
    session = get_session(provider.region)
    handler = OutputLookup.handle
    value = kwargs['ecrid']
    stack_name = context.get_fqn(value.split('::')[0])
    docker_file = kwargs['dockerfile']
    tag = kwargs['docker_tag']
    logger.info(f"Looking up ECR ID from {stack_name}")
    try:  # Exit early if the bucket's stack is already deleted
        session.client('cloudformation').describe_stacks(
            StackName=context.get_fqn(value.split('::')[0])
        )

    except ClientError as e:
        if 'does not exist' in e.response['Error']['Message']:
            logger.info('S3 bucket stack appears to have already been '
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

    #labels = {'commit': sha, 'buildtime': buildtime}
    # making labels blank to prevent many iterations of the same container with different labaels
    labels = {}
    path = kwargs.get('path', '.')
    build_kwargs = dict(tag=tag, docker_file=docker_file, labels=labels)
    if path:
        build_kwargs['path'] = path

    NPH.Docker_Helpers.docker_build_image(**build_kwargs)
    NPH.Docker_Helpers.ecr_push(session=session, tag=tag, ecr_name=ecr_name)

    return build_kwargs


if __name__ == '__main__':
    handler(context, provider, **kwargs)
