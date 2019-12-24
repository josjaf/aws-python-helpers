import os
import uuid
import zipfile
import botocore
import logging
import boto3


class Helpers():

    def __init__(self, *args, **kwargs):
        return

    def get_child_session(self, account_id, role_name, session=None):
        """
        get session, with error handling, allows for passing in an sts client. This allows Account A > B > C where A cannot assume a role directly to C
        :param self
        :param account_id:
        :param role_name:
        :param session=None:
        :return:
        """
        # '/' + name if not name.startswith('/') else name
        try:
            # allow for a to b to c if given sts client.
            if session == None:
                session = boto3.session.Session()

            client = session.client('sts')

            response = client.get_caller_identity()
            # remove the first slash
            role_name = role_name[1:] if role_name.startswith("/") else role_name
            # never have a slash in front of the role name
            role_arn = 'arn:aws:iam::' + account_id + ':role/' + role_name
            print("Creating new session with role: {} from {}".format(role_arn, response['Arn']))

            response = client.assume_role(
                RoleArn=role_arn,
                RoleSessionName=str(uuid.uuid1())
            )
            credentials = response['Credentials']
            session = boto3.Session(
                aws_access_key_id=credentials['AccessKeyId'],
                aws_secret_access_key=credentials['SecretAccessKey'],
                aws_session_token=credentials['SessionToken']
            )
            return session
        except botocore.exceptions.ClientError as e:

            if e.response['Error']['Code'] == 'AccessDenied':
                raise e
                # raise Exception(e)

            elif 'Not authorized to perform sts:AssumeRole' in str(e):
                raise e
                # raise Exception(f"ERROR:Not authorized to perform sts:AssumeRole on {role_arn}")
            else:
                print(e)
                # raise Exception(e)

        finally:
            pass

    def print_separator(self, text):
        print('\n' * 3)
        print("#" * 75)
        print(text)
        print("#" * 75)
        return

    def file_to_string(self, file_path):
        with open(file_path, 'r') as f:
            file_str = f.read()
            f.close()
        return file_str

    def dict_to_env_variables(self, dictionary):
        """
        Take a dictionary and export to environment variables
        :param dictionary:
        :return:
        """

        for key, value in dictionary.items():
            os.environ[key] = value

        return

    def check_s3_bucket_available(self, session, bucket_name):
        """
        check if s3 bucket is available for creating by a later function
        :param session:
        :param bucket_name:
        :return:
        """
        s3 = session.client('s3')
        try:
            response = s3.create_bucket(Bucket=bucket_name)
            response = s3.delete_bucket(Bucket=bucket_name)
            return response
        except botocore.exceptions.ClientError as e:
            print(e)

            if e.response['Error']['Code'] == 'BucketAlreadyExists':
                raise e
            if e.response['Error']['Code'] == 'AccessDenied':
                raise e
        return True

    def wildcard_delete(self, extension, directory='.'):
        assert extension, f"Got Blank Extension"
        for subdir, dirs, files in os.walk(directory):
            for file in files:

                full_path = (os.path.abspath(os.path.join(subdir, file)))
                if full_path.endswith(extension):
                    print(f"Removing {full_path}")
                    os.remove(full_path)
        return

    def create_zip_from_dir(self, dir_to_zip, zip_path=None, ignore_folder_root=True):
        # assert dir_to_zip is str, f"Create Zip needs String"
        ignored = ['.zip', '.pyc', '.tar', '.gz']

        # process zip path
        if not zip_path:
            zip_path = str('source.zip')

        if not zip_path.endswith('.zip'):
            zip_path = zip_path + '.zip'
        if not os.path.isabs(zip_path):
            zip_path = os.path.abspath(zip_path)
        print(f"Zip Path: {zip_path}")
        z = zipfile.ZipFile(zip_path, "w")

        path = os.path.abspath('.')
        path = os.path.join(path, zip_path)
        print(f"Creating Zip: {zip_path} of {dir_to_zip}")

        if dir_to_zip.startswith('~'):
            # raise RuntimeError('Tilde not suported')
            dir_to_zip = os.path.expanduser(dir_to_zip)
            print(dir_to_zip)
        if dir_to_zip.startswith('/'):
            print('got absolute path')

        original_dir = os.path.abspath(os.path.curdir)
        if ignore_folder_root:
            # default behavior, do not include prefix in the zip

            os.chdir(dir_to_zip)
            dir_to_zip = '.'
        # print(f"Current Directory: {os.path.abspath(os.curdir)}")
        for root, dirs, files in os.walk(dir_to_zip):

            # avoid infinite zip recursion
            for file in files:
                if file.endswith(tuple(ignored)): continue
                if file == zip_path: continue
                # print(os.path.join(root, file))
                z.write(os.path.join(root, file))
        z.close()
        # switch back to original working directory
        os.chdir(original_dir)
        return
