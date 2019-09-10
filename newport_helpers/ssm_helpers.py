import time
import boto3
import botocore

class SSMHelpers():
    def __init__(self, *args, **kwargs):
        return

    def command_waiter(self, session, command_id, instance_id):
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

    def get_parameter_startswith(self, session, parameter_name):
        ssm = session.client('ssm')
        response = ssm.describe_parameters()
        parameter_names = [p['Name'] for p in response['Parameters'] if p['Name'].startswith(parameter_name)]
        return parameter_names

    def get_parameter(self, paremeter_name, session):
        try:
            ssm = session.client('ssm')
            response = ssm.get_parameter(
                Name=paremeter_name,
            )
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'ParameterNotFound':
                return None
        except Exception as e:
            raise e

        return response
