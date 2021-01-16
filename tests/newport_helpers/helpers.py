import sys
import unittest
import newport_helpers
import moto
#import boto3
import botocore.exceptions
try:
    from unittest.mock import MagicMock, patch, ANY
except ImportError:
    import mock
    from mock import MagicMock, patch, ANY
import botocore
from botocore.exceptions import ClientError
import os, json
from importlib import import_module

CONFIG_CLIENT_MOCK = MagicMock()
STS_CLIENT_MOCK = MagicMock()
STS_SESSION_MOCK = MagicMock()
REGION = None

class Boto3Mock():
    @staticmethod
    def client(client_name, *args, **kwargs):
        if client_name == 'config':
            return CONFIG_CLIENT_MOCK
        if client_name == 'sts':
            return STS_CLIENT_MOCK

        raise Exception("Attempting to create an unknown client")

    @staticmethod
    def Session(region_name=None):
        global REGION
        REGION = region_name

        return STS_SESSION_MOCK

sys.modules['boto3'] = Boto3Mock()


class HelpersTest(unittest.TestCase):
    @unittest.mock.patch.dict('os.environ', {'PCA_ARN': 'testing'})
    def setUp(self):
        from newport_helpers import helpers
        Helpers = helpers.Helpers()
        rule = Helpers
        Code = Helpers

    def test_check_s3_bucket_available_not_exists(self):

        bucket_name = 'test-magic-mock'
        mocked_session = Boto3Mock.Session()
        #s3 = boto3.client('s3')
        #response = s3.create_bucket(Bucket=bucket_name)

        mocked_delete_response = {'HTTPStatusCode': 204}
        MOCKED_S3_CLIENT = MagicMock(return_value=mocked_session.client)


        test_args = dict(session=mocked_session, bucket_name=bucket_name)
        rule.check_s3_bucket_available = MagicMock(return_value=mocked_delete_response)

        response = rule.check_s3_bucket_available(**test_args)
        # check for delete response
        #response['HTTPStatusCode'] = 204
        assertEqual(response['HTTPStatusCode'], mocked_delete_response['HTTPStatusCode'])

    def test_check_s3_bucket_available_not_exists_exception(self):

        bucket_name = 'test-magic-mock'
        mocked_session = Boto3Mock.Session()
        #s3 = boto3.client('s3')
        #response = s3.create_bucket(Bucket=bucket_name)

        mocked_exception  = botocore.exceptions.ClientError(
            {'Error': {'Code': 'BucketAlreadyExists'}}, 'operation')
        MOCKED_S3_CLIENT = MagicMock(return_value=mocked_session.client)


        test_args = dict(session=mocked_session, bucket_name=bucket_name)
        try:
            rule.check_s3_bucket_available = MagicMock(side_effect=mocked_exception)
        except botocore.exceptions.ClientError:
            response = rule.check_s3_bucket_available(**test_args)
            assertRaises(botocore.exceptions.ClientError, rule.check_s3_bucket_available)
