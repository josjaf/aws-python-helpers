import math
import os
import newport_helpers
logger = newport_helpers.nph.logger

from botocore.exceptions import ClientError


def update_secret(session, secret_name, kms_key_id, key_data):
    """
    this could also parameterize secretstring vs secretbinary
    :param session:
    :param secret_name:
    :param kms_key_id:
    :param key_data:
    :return:
    """
    logger.info(f"Updating Secret {secret_name} with KMS Key: {kms_key_id}")
    secrets_manager = session.client('secretsmanager')
    response = secrets_manager.update_secret(
        SecretId=secret_name,
        KmsKeyId=kms_key_id,
        SecretString=key_data
    )
    logger.info(response)
    return response


def create_secret(session, secret_name, kms_key_id, key_data):
    """
    this could also parameterize secretstring vs secretbinary
    :param session:
    :param secret_name:
    :param kms_key_id:
    :param key_data:
    :return:
    """
    secrets_manager = session.client('secretsmanager')
    logger.info(f"Creating Secret {secret_name} with KMS Key: {kms_key_id}")
    response = secrets_manager.create_secret(
        Name=secret_name,
        # SecretBinary=key_data,
        KmsKeyId=kms_key_id,
        # ClientRequestToken='string',
        SecretString=key_data
    )
    logger.info(response)
    logger.info(f"Creating Secret {secret_name}")
    return response


def restore_secret(session, secret_name):
    secrets_manager = session.client('secretsmanager')
    response = secrets_manager.restore_secret(
        SecretId=secret_name
    )
    logger.info(f"Restoring Secret: {secret_name}")
    return response


def create_update_secret(session, secret_name, kms_key_id, key_data, index=0):
    """
    this function assumes you don't have any other permission besides create and update secret
    uses index to avoid infite recursion
    :param session:
    :param secret_name:
    :param kms_key_id:
    :param key_data:
    :param index:
    :return:
    """
    secrets_manager = session.client('secretsmanager')
    if index >= 5:
        raise Exception("Too many create update secret retries")
    try:
        response = create_secret(session, secret_name, kms_key_id, key_data)

    except ClientError as e:
        # logger.info(e)
        if e.response['Error']['Code'] == 'ResourceExistsException':
            # logger.info(f"ERROR, could not find existing secret")
            logger.info(f"Resource {secret_name} already exists, updating instead")
            response = update_secret(session, secret_name, kms_key_id, key_data)

        # if e.response['Error']['Code'] == 'InvalidRequestException'\
        #         and 'deleted' in e.response['Error']['Code'].lower():
        if e.response['Error']['Code'] == 'InvalidRequestException':
            logger.info(f"Secret {secret_name} is in deleted state")
            restore_secret(session, secret_name)
            index += 1
            # potential for broken recursion
            response = create_update_secret(session, secret_name, kms_key_id, key_data, index)

    except Exception as e:
        logger.info(e)
        raise e
    return response


def put_secret_chunks(file_path, session, namespace):
    """
    Get the Total Size of the parameters.
    :param file_path:
    :param ssm:
    :return:
    """
    # total size in bytes
    secrets_manager = session.client('secretsmanager')
    total_size = os.path.getsize(file_path)
    # max ssm parameter xstore size
    chunk_size = 4096
    total_chunks = (float(total_size) / chunk_size)

    # if the total size divided by the chunk size is a whole number, do not round up
    if total_chunks.is_integer():
        logger.info("RARE: Total Size divded by Chunk Size is a whole number")
    else:
        total_chunks = math.ceil(total_chunks)
    parameter_names = []

    # removing 1 from total chunks, instead of changing index to 1 otherwise index will never match total chunks, since index starts at 0
    total_chunks -= 1
    # do not add 1 if there is a 00 at the end
    logger.info("Splitting File into {} Total Chunks".format(total_chunks))
    index = 0
    # changed from binary
    # with open(file_path, 'rb') as infile:
    with open(file_path, 'r') as infile:
        while True:

            chunk = infile.read(chunk_size)
            logger.info(chunk)
            if not chunk:
                break
            logger.info("Chunk {}".format(index))

            parameter_name = "{}-{}".format(namespace, index)
            if index == total_chunks:
                parameter_name = "{}-{}-LAST".format(namespace, index)
            parameter_names.append(parameter_name)
            create_update_secret(session, parameter_name, chunk, 0)

            index += 1
        logger.info("New Parameters: {}".format(parameter_names))
    return


def get_secret(session, secret_name):
    # if version not specified, this will return the latest version
    secrets_manager = session.client('secretsmanager')
    try:
        get_secret_value_response = secrets_manager.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            logger.info("The requested secret " + secret_name + " was not found")
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            logger.info("The request was invalid due to:", e)
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            logger.info("The request had invalid params:", e)
            raise e
        else:
            logger.info(e)
            raise e
        # Decrypted secret using the associated KMS CMK
        # Depending on whether the secret was a string or binary, one of these fields will be populated
    if 'SecretString' in get_secret_value_response:
        secret = get_secret_value_response['SecretString']
        return secret
    else:
        binary_secret_data = get_secret_value_response['SecretBinary']
        return binary_secret_data


def delete_secret(session, secret_name):
    secrets_manager = session.client('secretsmanager')
    response = secrets_manager.delete_secret(
        SecretId=secret_name,
        RecoveryWindowInDays=7
    )
    return response


def get_all_secrets(session):
    secrets_manager = session.client('secretsmanager')
    secret_names = []

    response = secrets_manager.list_secrets()

    for secret in response['SecretList']:
        secret_names.append(secret['Name'])

    while 'NextToken' in response:
        response = secrets_manager.list_secrets(NextToken=response['NextToken'])
        for secret in response['SecretList']:
            secret_names.append(secret['Name'])

    return secret_names


def get_secret_startswith(session, secret_name):
    secrets_manager = session.client('secretsmanager')
    all_secrets = get_all_secrets(session)

    secret_startswith = [secret for secret in all_secrets if secret.startswith(secret_name)]
    return secret_startswith


def check_secret_status(session, secret_name):
    """

    :param session:
    :param secret_name:
    :return:
    """
    deleted = 'DELETED'
    active = 'ACTIVE'
    new = 'NEW'

    secrets_manager = session.client('secretsmanager')
    try:
        response = secrets_manager.describe_secret(SecretId=secret_name)

        if 'DeletedDate' in response:
            return deleted
        else:
            return active
    except ClientError as e:

        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            logger.info(f"Could not find secret: {secret_name}")
            return new

        if 'marked for deletion' in e.response['Error']['Message']:
            logger.info(f"Secret {secret_name} Deleted")
            return deleted
