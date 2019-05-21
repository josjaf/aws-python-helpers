"""Stacker hook for cleaning up resources prior to CFN stack deletion."""
# TODO Instead of writing a writing a post deploy and pre destroy stack for Org Trail, Create a regular trail via cloudformation, update the trail to make it an org trail as the post deploy, and then roll back the stack, no pre deploy hook required
import logging

import boto3
from botocore.exceptions import ClientError

from stacker.lookups.handlers.output import OutputLookup
from stacker.lookups.handlers.rxref import RxrefLookup
from stacker.lookups.handlers.xref import XrefLookup
from stacker.session_cache import get_session

LOGGER = logging.getLogger(__name__)


def handler(context, provider, **kwargs):
    # TODO get this from a previous stack, lookup or construct it
    """Delete objects in bucket."""

    if kwargs.get('trail_name'):
        bucket_name = kwargs['trail_name']
    else:
        if kwargs.get('output_lookup'):
            value = kwargs['output_lookup']
            handler = OutputLookup.handle
        elif kwargs.get('rxref_lookup'):
            value = kwargs['rxref_lookup']
            handler = RxrefLookup.handle
        elif kwargs.get('xref_lookup'):
            value = kwargs['xref_lookup']
            handler = XrefLookup.handle
        else:
            LOGGER.fatal('No bucket name/source provided.')
            return False
        stack_name = context.get_fqn(value.split('::')[0])
        print(stack_name)
        print(f"Deleting Bucket: from Stack: {stack_name}")

    trail_name = handler(
        value,
        provider=provider,
        context=context
    )
    #trail_name = kwargs.get('orgtrailarn')
    print(trail_name)






    session = get_session(provider.region)
    org_session = session





    ####
    #### Use this Code when constructing the Trail Arn in the
    ####
    # profile = kwargs.get('profile')
    # org_session = boto3.session.Session(profile_name=profile)

    # construct org trail arn
    #account_id = org_session.client('sts').get_caller_identity()['Account']
    #region = org_session.region_name
    #trail_arn = f"arn:aws:cloudtrail:{region}:{account_id}:trail/{context.environment['namespace']}"

    ####
    #### Use this Code when constructing the Trail Arn in the
    ####



    cloudtrail = org_session.client('cloudtrail')


    #trail_arn = kwargs.get('orgtrailarn')
    trail_arn = trail_name
    assert trail_arn is not None, f"Got bad trail arn"
    #trail_arn =
    print(trail_arn)
    try:
        response = cloudtrail.stop_logging(
            Name=trail_arn
        )
        response = cloudtrail.delete_trail(
            Name=trail_arn
        )
    except ClientError as e:

        if e.response['Error']['Code'] == 'InvalidTrailNameException':
            print(e)
    except Exception as e:
        print(e)
    return True
