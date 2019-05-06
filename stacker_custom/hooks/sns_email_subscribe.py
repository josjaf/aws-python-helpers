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
    # value = read_value_from_path(value)

    sts = boto3.client('sts')
    response = sts.get_caller_identity()
    hook_return = {}
    topic_arn = kwargs.get('SNSArn')
    emails = kwargs.get('emails')
    try:
        sns = boto3.client('sns')
        for email in emails.split(','):

            response = sns.subscribe(
                TopicArn=topic_arn,
                Protocol='email',
                Endpoint=email,

                ReturnSubscriptionArn=True
            )
        hook_return = {}
        return hook_return
    except Exception as e:
        print(e)
        raise e
    #     raise ValueError('EnvVar "{}" does not exist'.format(value))


if __name__ == '__main__':
    handler(context, provider, **kwargs)