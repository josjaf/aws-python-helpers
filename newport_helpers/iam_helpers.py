import csv
import os
import threading
import uuid
import zipfile
import boto3
import botocore

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