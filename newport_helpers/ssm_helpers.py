import time
import boto3


class SSMHelpers():
    def __init__(self, *args, **kwargs):
        return

    def command_waiter(self, session, command_id, instance_id):
        counter = 0
        ssm = session.client('ssm')
        finished_status = ['Delayed', 'Failed', 'Canceled', 'Success']
        running = True
        while running:
            time.sleep(1) # give the api time to register the command to avoid throwing an exception
            counter += 1
            response = ssm.get_command_invocation(CommandId=command_id, InstanceId=instance_id)
            if response['Status'] in finished_status:
                running = False
            time.sleep(10)
        return
