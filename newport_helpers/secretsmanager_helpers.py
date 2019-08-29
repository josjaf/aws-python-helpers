import hashlib
import logging
import math
import os
import pprint
import socket

from botocore.exceptions import ClientError


# def get_logger():
#     log_level = str(os.environ.get('LOG_LEVEL')).upper()
#     if log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
#         log_level = 'INFO'
#     logger = logging.getLogger()
#     logger.setLevel(log_level)
#     logger = logging.getLogger(__name__)
#     return logger


class SecretsManagerHelpers():
    def __init__(self, *args, **kwargs):
        return

    def update_secret(self, session, secret_name, key_data):
        print(f"Updating Secret {secret_name} with KMS Key: {os.environ.get('KMS_KEY_ID')}")
        asm = session.client('secretsmanager')
        response = asm.update_secret(
            SecretId=secret_name,
            KmsKeyId=os.environ.get('KMS_KEY_ID'),
            SecretString=key_data
        )
        pprint.pprint(response)
        return response

    def create_secret(self, session, secret_name, key_data):
        asm = session.client('secretsmanager')
        print(f"Creating Secret {secret_name} with KMS Key: {os.environ.get('KMS_KEY_ID')}")
        response = asm.create_secret(
            Name=secret_name,
            # SecretBinary=key_data,
            KmsKeyId=os.environ.get('KMS_KEY_ID'),
            # ClientRequestToken='string',
            SecretString=key_data
        )
        pprint.pprint(response)
        print(f"Creating Secret {secret_name}")
        return response

    def restore_secret(self, session, secret_name):
        asm = session.client('secretsmanager')
        response = asm.restore_secret(
            SecretId=secret_name
        )
        print(f"Restoring Secret: {secret_name}")
        return response

    def create_update_secret(self, session, secret_name, key_data, index):
        asm = session.client('secretsmanager')
        if not os.environ.get('KMS_KEY_ID', None):
            raise RuntimeError(f"os.environ['KMS_KEY_ID'] must be populated")
        if index >= 5:
            raise Exception("Too many create update secret retries")
        all_secrets = self.get_all_secrets(session)
        try:
            if secret_name in all_secrets:

                self.update_secret(asm, secret_name, key_data)
            else:

                self.create_secret(asm, secret_name, key_data)

        except ClientError as e:
            # print(e)
            # this should never run because we are now looking up the existing secrets before running create or update to avoid this exception / error
            if e.response['Error']['Code'] == 'ResourceExistsException':
                print(f"ERROR, could not find existing secret")
                print(f"Resource {secret_name} already exists, updating instead")
                self.update_secret(session, secret_name, key_data)

            # if e.response['Error']['Code'] == 'InvalidRequestException'\
            #         and 'deleted' in e.response['Error']['Code'].lower():
            if e.response['Error']['Code'] == 'InvalidRequestException':
                print(f"Secret {secret_name} is in deleted state")
                self.restore_secret(session, secret_name)
                index += 1
                # potential for broken recursion
                self.create_update_secret(session, secret_name, key_data, index)

        except Exception as e:
            print(e)
            raise e
        print()
        return

    def get_parameter_startswith(self, session, parameter_name):
        ssm = session.client('ssm')
        response = ssm.describe_parameters()
        parameter_names = [p['Name'] for p in response['Parameters'] if p['Name'].startswith(parameter_name)]
        return parameter_names

    def put_secret_chunks(self, file_path, session, namespace):
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
                self.create_update_secret(session, parameter_name, chunk, 0)

                index += 1
            print("New Parameters: {}".format(parameter_names))
        return

    def get_secret(self, session, secretsmanager, secret_name):
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

    def delete_secret(self, session, secret_name):
        asm = session.client('asm')
        response = asm.delete_secret(
            SecretId=secret_name,
            RecoveryWindowInDays=7
        )
        return

    def get_all_secrets(self, session):
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

    def get_secret_startswith(self, session, secret_name):
        asm = session.client('asm')
        all_secrets = self.get_all_secrets(session)

        secret_startswith = [secret for secret in all_secrets if secret.startswith(secret_name)]
        return secret_startswith


def write_string_to_file(string, file):
    with open(file, 'w') as f:
        f.write(string)
        f.close()
    print("Writing to file: {}".format(file))
    return


def file_to_string(file_path):
    with open(file_path, 'r') as f:
        file_str = f.read()
        f.close()
    return file_str