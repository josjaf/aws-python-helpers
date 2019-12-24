import csv
import os
import threading
import uuid
import zipfile
import boto3
import botocore
import re
import boto3


class IamHelpers():
    def __init__(self, *args, **kwargs):
        return

    def get_iam_roles(self, session):
        iam = session.client('iam')
        paginator = iam.get_paginator('list_roles')
        page_iterator = paginator.paginate()
        iam_roles = []
        for page in page_iterator:
            for role in page['Roles']:
                iam_roles.append(role['RoleName'])
        return iam_roles


    def check_iam_role_exists(self, session, role):
        iam_roles = self.get_iam_roles(session)
        if role in iam_roles:
            return True
        else:
            return False

    def split_role_arn(self, arn):
        account_id = arn.split(":")[4]
        role_name = re.sub(r"^role/", "/", arn.split(":")[5], 1)
        return account_id, role_name

    def sts_to_iam_arn(self, session):
        sts = session.client('sts')
        response_arn = sts.get_caller_identity()['Arn']
        # TODO FIX 'arn:aws:sts::253737654488:assumed-role/bk/josjaffe@amazon.com/botocore-session-1576812164'

        if ':user/' not in response_arn:
            if 'assumed-role' in response_arn:  # might mean there is a session
                response_arn = response_arn.replace("arn:aws:sts", "arn:aws:iam")
                response_arn = response_arn.replace("assumed-role", "role")
                constructed_arn = response_arn.rsplit("/", 1)[0]
            return constructed_arn
        else:
            return response_arn
