from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
import os
import boto3
import botocore

def put_public_key_pair(ec2, **kwargs):
    #response = ec2.describe_regions()

    #for region in response['Regions']:
    #ec2 = boto3.client('ec2', region_name=region['RegionName'])
    #print(f"Key Upload: {region['RegionName']}")
    try:
        public_key_name = kwargs.get('public_key_name')
        response = ec2.delete_key_pair(
            KeyName=public_key_name,
        )
        response = ec2.import_key_pair(
            KeyName=public_key_name,
            PublicKeyMaterial=kwargs.get('public_key_str')
        )

    except botocore.exceptions.ClientError as e:

        if e.response['Error']['Code'] == 'InvalidKeyPair':
            print(e)
    except Exception as e:
        print(e)
    return

def handler(provider, context, **kwargs):
    """Retrieve an environment variable.
    For example:
        # In stacker we would reference the environment variable like this:
        conf_key: ${envvar ENV_VAR_NAME}
        You can optionally store the value in a file, ie:
        $ cat envvar_value.txt
        ENV_VAR_NAME
        and reference it within stacker (NOTE: the path should be relative to
        the stacker config file):
        conf_key: ${envvar file://envvar_value.txt}
        # Both of the above would resolve to
        conf_key: ENV_VALUE
    """
    #value = read_value_from_path(value)
    results = {}
    region = kwargs.get('region')
    profile = kwargs.get('profile')

    if profile:
        session_params = {'profile_name': profile}
    if region:
        session_params['region_name'] = region

    session = boto3.session.Session(**session_params)

    ec2 = session.client('ec2')

    public_key_str = kwargs.get('public_key_str')
    public_key_name = kwargs.get('public_key_name')
    
    put_public_key_pair(ec2, **kwargs)
    results['public_key_str'] = kwargs.get('public_key_str')
    results['public_key_name'] = kwargs.get('public_key_name')
    return results
if __name__ == '__main__':
    handler(value=None)