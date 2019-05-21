from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
import os
import boto3
from botocore.exceptions import ClientError
from newport_helpers import helpers, cfn_helpers
Helpers = helpers.Helpers()
Cfn_helpers = cfn_helpers.CfnHelpers()

def prepare_org_account(session):
    organizations_client = session.client('organizations')
    try:
        response = organizations_client.enable_all_features()
    except ClientError as e:
        if e.response['Error']['Code'] == 'HandshakeConstraintViolationException' \
                and "All features are already enabled on this organization" in str(e):
            pass
    response = organizations_client.enable_aws_service_access(
        ServicePrincipal='cloudtrail.amazonaws.com'
    )
    return


def org_trail_enabled(cloudtrail, trail_name):
    response = cloudtrail.describe_trails()
    try:
        trails = [t for t in response['trailList'] if t['IsOrganizationTrail']]
        if not trails:
            return False

        org_trails = []
        for trail in trails:
            response = cloudtrail.get_trail_status(
                Name=trail['Name']
            )
            org_trails.append(response)

        # TODO Fix logging issue here, this is not the right way to check this

        enabled_org_trails = [t for t in org_trails if t['IsLogging']]
        if not enabled_org_trails:
            return False

        org_trail_with_matching_namespace = [t['Name'] for t in trails]

        # loggin_on_org_trails = []
        # trail_names = [t['Name'] for t in trails]
        # for trail in trail_names:
        #     response = cloudtrail.get_trail_status(
        #         Name=trail
        #     )
        if trail_name not in org_trail_with_matching_namespace:
            return False

        return True

    except KeyError:
        return False


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

    # helpers.print_separator('Looking up CloudTrail')
    helpers.print_separator('Deploying CloudTrail')
    print(f"11/20/2018, Start Trail with Org Trail Property is not available in CFN"
          f"https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudtrail-trail.html")

    org_session = boto3.session.Session(profile_name=context.environment['profile_org_master'])
    prepare_org_account(org_session)
    logging_account_session = boto3.session.Session(profile_name=context.environment['profile_logging_account'])

    cloudtrail = org_session.client('cloudtrail')
    cfn = logging_account_session.client('cloudformation')

    trail_name = f"{context.environment['namespace']}"
    print(trail_name)

    if org_trail_enabled(cloudtrail, trail_name):
        print(f"Org Trail already created and currently Logging, not running key template")
        return 'Org Trail already enabled'

    STACK_NAME = f"{context.environment['namespace']}-{context.environment['stack_name_cloudtrail_bucket_key']}"

    trail_kwargs = dict(
        Name=trail_name,
        S3BucketName=helpers.get_stack_output(cfn=cfn, stack_name=STACK_NAME, output='S3BucketName'),
        IncludeGlobalServiceEvents=True,
        IsMultiRegionTrail=True,
        EnableLogFileValidation=True,
        KmsKeyId=helpers.get_stack_output(cfn=cfn, stack_name=STACK_NAME, output='KMSKey'),
        IsOrganizationTrail=True)
    print(f"Trail Kwargs: {trail_kwargs}")
    try:

        response = cloudtrail.create_trail(**trail_kwargs)
        response = cloudtrail.start_logging(Name=trail_name)

    except ClientError as e:
        if e.response['Error']['Code'] == 'TrailAlreadyExistsException':
            print(f"Trail {trail_name} Already Exists")
            print(f"Starting Trail {trail_name}")
            response = cloudtrail.start_logging(Name=trail_name)
            print(response)
            pass
        else:
            raise e
    except Exception as e:
        print(e)
        raise e
    return trail_kwargs


if __name__ == '__main__':
    handler(context, provider, **kwargs)
