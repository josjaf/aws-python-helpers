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
        from newport_helpers import cfn_helpers
        CfnHelpers = cfn_helpers.CfnHelpers
        self.rule = CfnHelpers
        self.Code = CfnHelpers

    def test_dict_to_cfn_parameters(self):


        mocked_dict = {'App': 'Newport', 'Type': 'Helpers'}
        processed_list = [{'ParameterKey': 'App', 'ParameterValue': 'Newport'}, {'ParameterKey': 'Type', 'ParameterValue': 'Helpers'}]
        self.rule.dict_to_cfn_parameters = MagicMock(return_value=processed_list)
        #response = self.rule.dict_to_cfn_parameters(mocked_dict)
        response = self.rule.dict_to_cfn_parameters(mocked_dict)
        # check for delete response
        #response['HTTPStatusCode'] = 204
        self.assertEqual(response, processed_list)

    # def test_check_stack_set_exists(self):
    #
    #
    #     mocked_session = Boto3Mock.Session()
    #     self.rule.cfn_check_stack_exists = MagicMock(return_value=True)
    #     response = self.rule.cfn_check_stack_exists(session=mocked_session, stack_name='test')
    #     self.assertEqual(response, True)


if __name__ == "__main__":
    unittest.main()