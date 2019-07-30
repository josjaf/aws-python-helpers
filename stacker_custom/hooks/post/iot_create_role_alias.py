"""
  role_alias:
    path: role_alias.handler
    required: true
    enabled: true
    args:
      roleArn: role::RoleArn
      roleAlias: newport-iot

"""
import logging

from stacker.lookups.handlers.output import OutputLookup
from stacker.lookups.handlers.rxref import RxrefLookup
from stacker.lookups.handlers.xref import XrefLookup
from stacker.session_cache import get_session
from stacker.logger import setup_logging
from botocore.exceptions import ClientError

import boto3
import botocore

import datetime
from base64 import b64decode
logger = logging.getLogger(__name__)


def handler(context, provider, **kwargs):
    session = get_session(provider.region)
    handler = OutputLookup.handle
    value = kwargs['roleArn']
    stack_name = context.get_fqn(value.split('::')[0])
    logger.info(f"Looking up Arn from {stack_name}")
    try:  # Exit early if the bucket's stack is already deleted
        session.client('cloudformation').describe_stacks(
            StackName=context.get_fqn(value.split('::')[0])
        )

    except ClientError as e:
        raise e
    roleArn = handler(
        value,
        provider=provider,
        context=context
    )

    iot = session.client('iot')
    try:
        response = iot.create_role_alias(
            roleAlias=kwargs.get('roleAlias'),
            roleArn=roleArn,
            credentialDurationSeconds=900
        )
        print(response)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ResourceAlreadyExistsException':
            print("Iot Alias already exists")
            return {'status': 'already exists'}
    except Exception as e:
        print(e)
        raise e
    hook_return = {'buildStatus': 'success'}
    return hook_return


if __name__ == '__main__':
    handler(context, provider, **kwargs)

