from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
import os
import boto3
import logging

from botocore.exceptions import ClientError

from stacker.lookups.handlers.output import OutputLookup
from stacker.lookups.handlers.rxref import RxrefLookup
from stacker.lookups.handlers.xref import XrefLookup
from stacker.lookups.handlers.envvar import EnvvarLookup
from stacker.session_cache import get_session



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
    """
    Sample yaml
    post_build:
  - path: stacker_custom.hooks.sns_email_subscribe.handler
    required: true
    enabled: true
    data_key: email_subscribe
    args:
      list_of_emails_var: emails
      sns_rxref_lookup: base::SNSArn
      #sample: ${output pipeline::PipelineName}
      profile: ${profile_shared_account}
      
      
    """
    # value = read_value_from_path(value)

    hook_return = {}
    print(kwargs)
    print(context)
    topic_arn = kwargs.get('sns_rxref_lookup')
    emails = kwargs.get('list_of_emails_var')



    value = kwargs['sns_rxref_lookup']
    sns_arn = RxrefLookup.handle(
        value,
        provider=provider,
        context=context
    )


    value = kwargs['list_of_emails_var']
    emails = EnvvarLookup.handle(
        value,
        provider=provider,
        context=context
    )
    #import pdb; pdb.set_trace()
    hook_returns = []
    try:
        sns = boto3.client('sns')
        for email in emails.split(','):
            print(email)
            response = sns.subscribe(
                TopicArn=sns_arn,
                Protocol='email',
                Endpoint=email,

                ReturnSubscriptionArn=True
            )
            print(response)
        hook_return = {'response': response}
        return hook_return
    except Exception as e:
        print(e)
        raise e
    #     raise ValueError('EnvVar "{}" does not exist'.format(value))


if __name__ == '__main__':
    handler(context, provider, **kwargs)