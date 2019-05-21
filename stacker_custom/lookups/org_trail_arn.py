from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
import boto3
import botocore
import os

from stacker.lookups.handlers import LookupHandler

TYPE_NAME = "envvar"


class Arn(LookupHandler):
    @classmethod
    def handle(cls, value, context, provider, **kwargs):


        org_session = boto3.session.Session(profile_name=context.environment['profile_org_master'])
        org_client = org_session.client('organizations')
        # Dynammic Lookup
        # sts = org_session.client('sts')
        # org_account_id = sts.get_caller_identity()['Account']
        # Config File

        org_account_id = context.environment['account_id_org_master']
        namespace = context.environment['namespace']
        print(F"Namespace: {namespace}")
        logging_account_id = context.environment['namespace']
        region = context.environment['region']
        arn = f"arn:aws:cloudtrail:{region}:{org_account_id}:trail/{namespace}"
        print(f"CloudTrail Arn: {arn}")


        try:
            return arn
        except KeyError:
            raise ValueError('Var "{}" does not exist'.format(value))