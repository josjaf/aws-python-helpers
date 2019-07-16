"""
post_build:
  codebuild_waiter:
    path: stacker_custom.hooks.post.codebuild_waiter.handler
    required: true
    args:
      projectName: ecr::ecrid


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

NPH = newport_helpers.NPH()

logger = logging.getLogger(__name__)


def handler(context, provider, **kwargs):
    session = get_session(provider.region)
    handler = OutputLookup.handle
    value = kwargs['projectName']
    stack_name = context.get_fqn(value.split('::')[0])
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
    projectName = handler(
        value,
        provider=provider,
        context=context
    )

    cb = session.client('codebuild')

    response = cb.start_build(projectName=projectName)

    buildId = response['build']['id']
    NPH = newport_helpers.NPH()

    NPH.CodeBuild_Helpers.codebuild_job_waiter(session, buildId)

    return response


if __name__ == '__main__':
    handler(context, provider, **kwargs)
