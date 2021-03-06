import botocore
from . import log_helpers
logger = log_helpers.get_logger()

def get_provisioning_artifact_id(session, prod_id):
    ''' Query for Provisioned Artifact Id '''

    pa_list = list()
    service_catalog = session.client('servicecatalog')
    try:
        pa_list = service_catalog.describe_product_as_admin(Id=prod_id)['ProvisioningArtifactSummaries']
    except Exception as exe:
        raise RuntimeError("Unable to find the Provisioned Artifact Id: " + str(exe))

    if len(pa_list) > 0:
        output = pa_list[-1]['Id']
    else:
        raise RuntimeError("Unable to find the Provisioned Artifact Id: " + str(pa_list))

    return output


def get_launch_path(session, prod_id):
    service_catalog = session.client('servicecatalog')
    try:
        response = service_catalog.list_launch_paths(
            ProductId=prod_id)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            logger.info("Launch Path not found")
    return response
