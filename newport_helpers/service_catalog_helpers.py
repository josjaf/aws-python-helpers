import botocore
import newport_helpers
logger = newport_helpers.nph.logger
import time


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
    """

    :param session:
    :param prod_id:
    :return:
    """
    service_catalog = session.client('servicecatalog')
    try:
        response = service_catalog.list_launch_paths(
            ProductId=prod_id)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            logger.info("Launch Path not found")
    return response


def wait_for_provisioned_product(session, provisioned_product_id):
    """
    wait for a provisioned product id
    :param session:
    :param provisioned_product_id:
    :return:
    """
    service_catalog = session.client('servicecatalog')
    counter = 0
    sleep_time = 60
    # 'AVAILABLE'|'UNDER_CHANGE'|'TAINTED'|'ERROR'|'PLAN_IN_PROGRESS'
    pp_status = 'UNDER_CHANGE'
    while pp_status == 'UNDER_CHANGE' or pp_status == 'PLAN_IN_PROGRESS':
        logger.info(f"Sleeping for {sleep_time}, waiting for ProvisionedProductId: {provisioned_product_id}")
        time.sleep(sleep_time)

        # pp_status = get_provisioned_product_status(provisioned_product_name)
        counter += 1
        response = service_catalog.describe_provisioned_product(
            Id=provisioned_product_id
        )
        pp_status = response['ProvisionedProductDetail']['Status']
        logger.info(f"Waiting for {counter * sleep_time}")
        if pp_status == 'AVAILABLE':
            logger.info(f"SUCCESS: Product: {provisioned_product_id} is {pp_status}")
            break
        if pp_status == 'ERROR':
            raise Exception(f"ProvisionedProduct Stack: {provisioned_product_id} ERROR")
        if counter > 90:
            logger.info(f"ProvisionedProduct Stack: {provisioned_product_id} failed out of counter")
            raise Exception(f"ProvisionedProduct Stack: {provisioned_product_id} failed out of counter")
        if pp_status == "TAINTED":
            logger.info(f"Product: {provisioned_product_id} is {pp_status}")
            break
            # TODO Determine whether or not to break here
    return provisioned_product_id


def search_provisioned_product_full_list(session):
    """
    Get complete list of provisioned products
    :param session:
    :return:
    """
    service_catalog = session.client('servicecatalog')
    pp_list = list()
    filters = {"Key": "Account", "Value": "self"}

    try:
        pp_dict = service_catalog.search_provisioned_products(AccessLevelFilter=filters)
        pp_list = pp_dict['ProvisionedProducts']
    except Exception as e:
        raise e

    while 'NextPageToken' in pp_dict:
        next_token = pp_dict['NextPageToken']
        try:
            pp_dict = service_catalog.search_provisioned_products(AccessLevelFilter=filters, \
                                                                  PageToken=next_token)
            pp_list += pp_dict['ProvisionedProducts']
        except Exception as e:
            raise Exception('Failed to get complete provisioned products list: ' + str(e))

    return pp_list


def get_provisioned_product_status(session, prov_prod_name):
    """
    Query and return the Provisioned Product Current Status
    :param session:
    :param prov_prod_name:
    :return:
    """

    output = None
    service_catalog = session.client('servicecatalog')
    pp_list = service_catalog.gsearch_provisioned_product_full_list(session)

    for item in pp_list:
        if item['Name'] == prov_prod_name:
            output = item['Status']
            break

    if not output:
        raise RuntimeError('Unable to find any provisioned products: ' + str(prov_prod_name))

    return output
