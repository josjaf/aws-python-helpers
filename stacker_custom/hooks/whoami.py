from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
import os
import boto3



def handler(context, provider, **kwargs):
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
    
    sts = boto3.client('sts')
    response = sts.get_caller_identity()
    hook_return = {}
    try:
        response_arn = response['Arn']
        if ':user/' not in response_arn:
            response_arn = response_arn.replace("arn:aws:sts", "arn:aws:iam")
            response_arn = response_arn.replace("assumed-role", "role")
            constructed_arn = response_arn.rsplit("/", 1)[0]
            hook_return['Arn'] = constructed_arn
        else:
            hook_return['Arn'] = response['Arn']

        return hook_return
    except Exception as e:
        print(e)
        raise e
    #     raise ValueError('EnvVar "{}" does not exist'.format(value))
if __name__ == '__main__':
    handler(context, provider, **kwargs)