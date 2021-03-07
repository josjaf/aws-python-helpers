import time

import boto3
import botocore
from newport_helpers import log_helpers

logger = log_helpers.get_logger()


def command_waiter(session, command_id, instance_id):
    """
    Wait for an ssm command to hit the finished status
    :param session:
    :param command_id:
    :param instance_id:
    :return:
    """
    counter = 0
    ssm = session.client('ssm')
    finished_status = ['Delayed', 'Failed', 'Canceled', 'Success']
    running = True
    while running:
        time.sleep(1)  # give the api time to register the command to avoid throwing an exception
        counter += 1
        response = ssm.get_command_invocation(CommandId=command_id, InstanceId=instance_id)
        if response['Status'] in finished_status:
            running = False
        time.sleep(10)
    return


def get_parameters(session):
    """
    get all the parameters using the paginator, but returns the same response structure as if we used the next token
    response['Parameters']
    :param session:
    :return:
    """
    ssm = session.client('ssm')
    response = {}
    response['Parameters'] = []
    paginator = ssm.get_paginator('describe_parameters')
    response_iterator = paginator.paginate()

    for page in response_iterator:
        for s in page['Parameters']:
            response['Parameters'].append(s)

    return response


def get_parameter_startswith(session, parameter_name):
    """
    :param session:
    :param parameter_name:
    :return:
    """
    response = get_parameters(session)

    # response = ssm.describe_parameters()
    parameter_names = [p['Name'] for p in response['Parameters'] if p['Name'].startswith(parameter_name)]
    return parameter_names


def get_parameter(session, parameter_name):
    """
    Get a parameter, if it doesn't exist, catch the exception and return None
    Return the dict response and the value in a tuple
    :param session:
    :param parameter_name:
    :return:
    """
    try:
        logger.info(f"Getting Parameter: {parameter_name}")
        ssm = session.client('ssm')
        response = ssm.get_parameter(
            Name=parameter_name,
        )
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ParameterNotFound':
            return None
    except Exception as e:
        raise e

    return response, response['Parameter']['Value']


if __name__ == '__main__':
    session = boto3.session.Session()
    response = get_parameters(session)
    logger.info(response)
    params = get_parameter_startswith(session, '/')
    logger.info(params)
