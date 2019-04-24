from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
import boto3
import botocore

from stacker.lookups.handlers import LookupHandler


TYPE_NAME = "PrincipalOrgIdLookup"


class PrincipalOrgIdLookup(LookupHandler):
    @classmethod
    def handle(cls, value, context, provider, **kwargs):
        """Principal Org ID Lookup
        stacker.yaml

        lookups:
        principal_org_id: custom.lookups.principal_org_id.PrincipalOrgIdLookup

        """
        region = kwargs.get('region')
        profile = kwargs.get('profile')
        print(f"Kwags: {kwargs}")
        if profile:
            session = boto3.session.Session(profile_name=profile)
        else:
            session = boto3.session.Session()

        try:
            organizations = session.client('organizations')
            response = organizations.describe_organization()

            principal_org_id = response['Organization']['Id']
            print(principal_org_id)
            params = {"PrincipalOrgID": principal_org_id}

            print(f"Stacker Custom Lookup: Adding Principal Org Id: {params}")
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'AWSOrganizationsNotInUseException':
                raise RuntimeError("ACCOUNT NOT IN ORGANIZATION. CREATE A NEW ORGANIZATION IN ACCOUNT OR JOIN TO CONTINUE")
        except Exception as e:
            raise e


        try:
            return principal_org_id
        except KeyError:
            raise ValueError('EnvVar "{}" does not exist'.format(value))