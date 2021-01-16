import hashlib
import logging
import math
import os
import pprint
import socket

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
    print(f"Updating Secret {secret_name} with KMS Key: {kms_key_id}")
    asm = session.client('secretsmanager')
    response = asm.update_secret(
        SecretId=secret_name,
        KmsKeyId=kms_key_id,
        SecretString=key_data
    )
    pprint.pprint(response)
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
    asm = session.client('secretsmanager')
    print(f"Creating Secret {secret_name} with KMS Key: {kms_key_id}")
    response = asm.create_secret(
        Name=secret_name,
        # SecretBinary=key_data,
        KmsKeyId=kms_key_id,
        # ClientRequestToken='string',
        SecretString=key_data
    )
    pprint.pprint(response)
    print(f"Creating Secret {secret_name}")
    return response

def restore_secret(session, secret_name):
    asm = session.client('secretsmanager')
    response = asm.restore_secret(
        SecretId=secret_name
    )
    print(f"Restoring Secret: {secret_name}")
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
    asm = session.client('secretsmanager')
    if index >= 5:
        raise Exception("Too many create update secret retries")
    try:
        create_secret(asm, secret_name, key_data)

    except ClientError as e:
        # print(e)
        if e.response['Error']['Code'] == 'ResourceExistsException':
            # print(f"ERROR, could not find existing secret")
            print(f"Resource {secret_name} already exists, updating instead")
            update_secret(session, secret_name, kms_key_id, key_data)

        # if e.response['Error']['Code'] == 'InvalidRequestException'\
        #         and 'deleted' in e.response['Error']['Code'].lower():
        if e.response['Error']['Code'] == 'InvalidRequestException':
            print(f"Secret {secret_name} is in deleted state")
            restore_secret(session, secret_name)
            index += 1
            # potential for broken recursion
            create_update_secret(session, secret_name, kms_key_id, key_data, index)

    except Exception as e:
        print(e)
        raise e
    print()
    return

def put_secret_chunks(file_path, session, namespace):
    """
    Get the Total Size of the parameters.
    :param file_path:
    :param ssm:
    :return:
    """
    # total size in bytes
    asm = session.client('asm')
    total_size = os.path.getsize(file_path)
    # max ssm parameter store size
    chunk_size = 4096
    total_chunks = (float(total_size) / chunk_size)

    # if the total size divided by the chunk size is a whole number, do not round up
    if total_chunks.is_integer():
        print("RARE: Total Size divded by Chunk Size is a whole number")
    else:
        total_chunks = math.ceil(total_chunks)
    parameter_names = []

    # removing 1 from total chunks, instead of changing index to 1 otherwise index will never match total chunks, since index starts at 0
    total_chunks -= 1
    # do not add 1 if there is a 00 at the end
    print("Splitting File into {} Total Chunks".format(total_chunks))
    index = 0
    # changed from binary
    # with open(file_path, 'rb') as infile:
    with open(file_path, 'r') as infile:
        while True:

            chunk = infile.read(chunk_size)
            print(chunk)
            if not chunk:
                break
            print("Chunk {}".format(index))

            parameter_name = "{}-{}".format(namespace, index)
            if index == total_chunks:
                parameter_name = "{}-{}-LAST".format(namespace, index)
            parameter_names.append(parameter_name)
            create_update_secret(session, parameter_name, chunk, 0)

            index += 1
        print("New Parameters: {}".format(parameter_names))
    return

def get_secret(session, secret_name):
    # if version not specified, this will return the latest version
    asm = session.client('asm')
    try:
        get_secret_value_response = asm.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print("The requested secret " + secret_name + " was not found")
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            print("The request was invalid due to:", e)
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            print("The request had invalid params:", e)
            raise e
    else:
        # Decrypted secret using the associated KMS CMK
        # Depending on whether the secret was a string or binary, one of these fields will be populated
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            return secret
        else:
            binary_secret_data = get_secret_value_response['SecretBinary']
            return binary_secret_data
    return

def delete_secret(session, secret_name):
    asm = session.client('asm')
    response = asm.delete_secret(
        SecretId=secret_name,
        RecoveryWindowInDays=7
    )
    return response

def get_all_secrets(session):
    asm = session.client('asm')
    secret_names = []

    response = asm.list_secrets()

    for secret in response['SecretList']:
        secret_names.append(secret['Name'])

    while 'NextToken' in response:
        response = asm.list_secrets(NextToken=response['NextToken'])
        for secret in response['SecretList']:
            secret_names.append(secret['Name'])

    return secret_names

def get_secret_startswith(session, secret_name):
    asm = session.client('asm')
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

    asm = session.client('asm')
    try:
        response = asm.describe_secret(SecretId=secret_name)

        if 'DeletedDate' in response:
            return deleted
        else:
            return active
    except ClientError as e:

        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"Could not find secret: {secret_name}")
            return new

        if 'marked for deletion' in e.response['Error']['Message']:
            print(f"Secret {secret_name} Deleted")
            return deleted
