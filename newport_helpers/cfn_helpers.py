import boto3
from newport_helpers import helpers
import botocore
import uuid
import datetime
import time


class CfnHelpers():
    def __init__(self, *args, **kwargs):
        return

    def dict_to_cfn_parameters(self, parameters):
        """
        take a dict of cfn parameters and return a list of dicts for the cfn api
        :param parameters:
        :return:
        """
        parameters = [{"ParameterKey": k, "ParameterValue": v} for k, v in parameters.items()]
        return parameters

    def stack_create_update_waiter(self, cfn, args):
        """
        Wrapper function around waiters to determine which waiter to use - CREATE/UPDATE
        :param cfn:
        :param args:
        :return:
        """
        stack_exists = self.cfn_check_stack_exists(cfn, args['StackName'])
        if stack_exists:
            response = self.cloudformation_waiter(cfn, 'stack_update_complete', args['StackName'])
        else:
            response = self.cloudformation_waiter(cfn, 'stack_create_complete', args['StackName'])
        return response

    def cfn_check_stack_exists(self, session, stack_name):
        """
        return a bool based on whether stack exists or not
        :param cfn:
        :param stack_name:
        :return:
        """
        # TODO This may not be working correctly
        # TODO It's paginatination. I could look for all of the good stack status, but that still only works for 100 stacks
        # response = cfn.list_stacks()
        cfn = session.client('cloudformation')
        paginator = cfn.get_paginator('list_stacks')
        response_iterator = paginator.paginate(StackStatusFilter=[
            'CREATE_IN_PROGRESS', 'CREATE_FAILED', 'CREATE_COMPLETE', 'ROLLBACK_IN_PROGRESS', 'ROLLBACK_FAILED',
            'ROLLBACK_COMPLETE', 'DELETE_IN_PROGRESS', 'DELETE_FAILED', 'UPDATE_IN_PROGRESS',
            'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS', 'UPDATE_COMPLETE', 'UPDATE_ROLLBACK_IN_PROGRESS',
            'UPDATE_ROLLBACK_FAILED', 'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS', 'UPDATE_ROLLBACK_COMPLETE',
            'REVIEW_IN_PROGRESS',
        ])
        # removing delete complete
        # 'DELETE_COMPLETE',
        response = {}
        response['StackSummaries'] = []
        for page in response_iterator:
            for s in page['StackSummaries']:
                response['StackSummaries'].append(s)

        bad_stack_status = ['ROLLBACK_COMPLETE', 'ROLLBACK_IN_PROGRESS', 'CREATE_FAILED', 'UPDATE_ROLLBACK_IN_PROGRESS',
                            'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS']

        stackList = [stack['StackName'] for stack in response['StackSummaries'] if
                     stack['StackStatus'] in bad_stack_status]
        if stack_name in stackList:
            print("Stack: {} in ROLLBACK_COMPLETE. Cannot Continue. ERROR".format(stack_name))

        good_stack_status = ['CREATE_IN_PROGRESS', 'CREATE_COMPLETE', 'UPDATE_COMPLETE', 'UPDATE_ROLLBACK_COMPLETE']
        stackList = [stack['StackName'] for stack in response['StackSummaries'] if
                     stack['StackStatus'] in good_stack_status]
        # logger.info(stackList)
        if stack_name in stackList:
            return True
        else:
            return False
    def cloudformation_waiter(self, client, waiter, stack_name):
        now = datetime.datetime.now()

        waiter = client.get_waiter(waiter)
        waiter.wait(
            StackName=stack_name,
            WaiterConfig={
                'Delay': 30,
                'MaxAttempts': 15
            }
        )
        #print(f"Stack: {stack_name}, waiter: {waiter}")
        complete = datetime.datetime.now()
        diff = complete-now
        # Time will always be in multiples of the sleep
        #print(f"Stack: {stack_name} took {diff.seconds} to {waiter})")
        return
    def stack_complete(self, session, stack_name):
        """
        Wait for stack to complete, without using a waiter - will raise an exception if the stack fails to create or update, which is why we don't use a waiter for this.
        :param cloudformation_client:
        :param stack_name:
        :return:
        """
        # wait for stack to register in api first
        #cloudformation_waiter(cloudformation_client, 'stack_exists', stack_name)
        cloudformation_client = session.client('cloudformation')
        status = None
        counter = 0
        start = datetime.datetime.now()
        while status is not "CREATE_COMPLETE" or status is not "UPDATE_COMPLETE":
            response = cloudformation_client.describe_stacks(
                StackName=stack_name,
            )
            stack = response['Stacks'][0]
            status = stack['StackStatus']
            if status == 'UPDATE_COMPLETE' or status == 'CREATE_COMPLETE':
                print(f"Stack: {stack_name} with Status: {status} in Region: {cloudformation_client.meta.region_name}")
                break
            # status based rollback
            if status == 'ROLLBACK_IN_PROGRESS':

                print("Cloudformation Stack: {} failed to Rollback in Progress".format(stack_name))
                raise RuntimeError(f"Stack: {stack_name} with Status: {status} in Region: {cloudformation_client.meta.region_name}")
            # if status == 'CREATING':
            #     print("Cloudformation Stack: {} CREATING".format(stack_name))
            #     time.sleep(10)
            #     counter += 1
            failing_stack_status = ['ROLLBACK_COMPLETE', 'ROLLBACK_IN_PROGRESS', 'CREATE_FAILED', 'UPDATE_ROLLBACK_IN_PROGRESS','UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS']
            if status in failing_stack_status:
                print(f"Cloudformation Stack: {stack_name} FAILING STACK STATUS: {status}")
                raise RuntimeError(f"Stack: {stack_name} with FAILING Stack Status: {status} in Region: {cloudformation_client.meta.region_name}")

            else:
                time.sleep(10)
                counter += 1
                # time based rollback- if stack takes longer than x, roll back
                if counter > 120:
                    print("Cloudformation Stack: {} failed to Update or Create".format(stack_name))
                    raise Exception("Cloudformation Stack: {} failed to Update or Create".format(stack_name))

        # if 'LastUpdatedTime' in stack:
        #     start = stack['LastUpdatedTime']
        # else:
        #     start = stack['CreationTime']
        # describe stack events to determine the last one
        complete = datetime.datetime.now()
        diff = complete-start
        #TODO Fix time handling, currently time is in multiples of the sleep

        print(f"Stack: {stack_name} took {diff.seconds} seconds")
        return status
    def create_update_stack(self, session, args):
        """
        Wrapper for create update stack
        :param cloudformation_client:
        :param args:
        :return:
        """
        cloudformation_client = session.client('cloudformation')
        print("Stack: {} : Creating or Updating in Region: {}".format(args['StackName'], cloudformation_client.meta.region_name))
        stack_exists = self.cfn_check_stack_exists(session, args['StackName'])
        args['Capabilities'] = ['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM']
        print(f"Stack: {args['StackName']} Exists Status: {stack_exists}")
        if stack_exists:
            response = self.cfn_update_stack(session, args)
        else:
            response = self.cfn_create_stack(session, args)
        return response

    def cfn_create_stack(self, session, params):
        """
        Create a stack in cfn, but catch exceptions if the stack already exists
        :param client:
        :param params:
        :return:
        """
        client = session.client('cloudformation')
        # TODO Check if this function is properly getting called
        print("Stack: {} CREATING".format(params['StackName']))
        try:
            response = client.create_stack(**params)
            return response
            # print(response)

        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'AlreadyExistsException' \
                    and "already exists" in str(e):
                print(f"Stack: {params['StackName']} already exists, attempting to update")
                return None

            else:
                raise e
        except Exception as e:
            raise e

    def cfn_update_stack(self, session, params):
        """
        Update a Stack
        :param session:
        :param params:
        :return:
        """
        print("Stack: {} UPDATING".format(params['StackName']))
        client = session.client('cloudformation')
        try:
            response = client.update_stack(**params)
            print(response)
            return response
            # print(response)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'ValidationError' \
                    and "No updates are to be performed." in str(e):

                print("Stack: {} has no updates to be performed".format(params['StackName']))
                return e.response

            elif e.response['Error']['Code'] == 'ValidationError' and \
                    'is in UPDATE_IN_PROGRESS state and can not be updated' in str(e):
                print("Stack: {} has is already in UPDATE_IN_PROGRESS, nothing to do.".format(params['StackName']))
                return e.response

            elif e.response['Error']['Code'] == 'ValidationError' and \
                    'is in CREATE_IN_PROGRESS state and can not be updated' in str(e):
                print("Stack: {} has is already in CREATE_IN_PROGRESS, nothing to do.".format(params['StackName']))
                return e.response

            else:
                raise e
            return e.response
    def cfn_check_stack_exists(self, session, stack_name):
        """
        return a bool based on whether stack exists or not
        :param cfn:
        :param stack_name:
        :return:
        """
        # TODO This may not be working correctly
        # TODO It's paginatination. I could look for all of the good stack status, but that still only works for 100 stacks
        # response = cfn.list_stacks()
        cfn = session.client('cloudformation')
        paginator = cfn.get_paginator('list_stacks')
        response_iterator = paginator.paginate(StackStatusFilter=[
            'CREATE_IN_PROGRESS', 'CREATE_FAILED', 'CREATE_COMPLETE', 'ROLLBACK_IN_PROGRESS', 'ROLLBACK_FAILED', 'ROLLBACK_COMPLETE', 'DELETE_IN_PROGRESS', 'DELETE_FAILED',  'UPDATE_IN_PROGRESS', 'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS', 'UPDATE_COMPLETE', 'UPDATE_ROLLBACK_IN_PROGRESS', 'UPDATE_ROLLBACK_FAILED', 'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS', 'UPDATE_ROLLBACK_COMPLETE', 'REVIEW_IN_PROGRESS',
        ])
        # removing delete complete
        #'DELETE_COMPLETE',
        response = {}
        response['StackSummaries'] = []
        for page in response_iterator:
            for s in page['StackSummaries']:
                response['StackSummaries'].append(s)



        bad_stack_status = ['ROLLBACK_COMPLETE', 'ROLLBACK_IN_PROGRESS', 'CREATE_FAILED', 'UPDATE_ROLLBACK_IN_PROGRESS','UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS']


        stackList = [stack['StackName'] for stack in response['StackSummaries'] if stack['StackStatus'] in bad_stack_status]
        if stack_name in stackList:
            print("Stack: {} in ROLLBACK_COMPLETE. Cannot Continue. ERROR".format(stack_name))


        good_stack_status = ['CREATE_IN_PROGRESS', 'CREATE_COMPLETE', 'UPDATE_COMPLETE', 'UPDATE_ROLLBACK_COMPLETE']
        stackList = [stack['StackName'] for stack in response['StackSummaries'] if stack['StackStatus'] in good_stack_status]
        # logger.info(stackList)
        if stack_name in stackList:
            return True
        else:
            return False
    def stack_set_exists_check(self, session, stack_set_name):

        # TODO Add Pagination
        cfn = session.client('cloudformation')
        response = cfn.list_stack_sets(
            # NextToken='string',
            MaxResults=100,
            Status='ACTIVE'
        )
        stack_sets = [s['StackSetName'] for s in response['Summaries']
                      if s['StackSetName'] == stack_set_name]
        if stack_set_name in stack_sets:
            return True
        else:
            return False
    def get_stack_output(self, session, stack_name, output):

        cfn = session.client('cloudformation')
        response = cfn.describe_stacks()
        # print(f"Getting Output {output} from {stack_name}")
        try:
            stack = [s for s in response['Stacks'] if s['StackName'] == stack_name][0]
        except IndexError:
            raise Exception(f"Stack Name {stack_name} for output does not exist")
        # print(f"response: {stack}")
        if 'Outputs' not in stack:
            print(f"Outputs not found in {stack_name}")
            #raise RuntimeError(f"Outputs not found in {stack_name}")
            return None
        # print(stack['Outputs'])
        try:
            output_value = [o['OutputValue'] for o in stack['Outputs'] if o['OutputKey'] == output][0]
        except:
            #Exception
            print(f"Could not find output {output} in {stack_name}")
            raise RuntimeError(f"Could not find output {output} in {stack_name}")
        return output_value
    def get_stack_set_operations(self, client_session, stack_set_name, inprogress_status):
        """
        :param client_session:
        :param stack_set_name:
        :param inprogress_status:
        :return:
        """
        stack_set_operations = []
        paginator = client_session.get_paginator('list_stack_set_operations')
        try:
            response_iterator = paginator.paginate(
                StackSetName=stack_set_name,
            )
            for page in response_iterator:
                for summary in page['Summaries']:
                    stack_set_operations.append(summary)
        # stack set does not already exist
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'StackSetNotFoundException':
                return False

        inprogress_operations = [s for s in stack_set_operations if s['Status'] in inprogress_status]
        return inprogress_operations

    def operation_id_waiter(self, session, stack_name, operation_response):
        """
        call this after an update or create operation, this will wait for the operation id to show up
        :param session:
        :param stack_name:
        :param operation_response:
        :return:
        """
        cfn = session.client('cloudformation')
        inprogress_status = ['RUNNING', 'STOPPING']
        op_id = operation_response['OperationId']
        op_in_stack_list = False
        while not op_in_stack_list:
            for operation in self.get_stack_set_operations(cfn, stack_name, inprogress_status):
                if operation['OperationId'] == op_id:
                    print(f'Stack Set Operation {op_id} is in stack list')
                    op_in_stack_list = True
                else:
                    print(f'Operation: {op_id} not present, sleeping...')
                    time.sleep(5)
        op_busy = True
        loop_count = 0
        while op_busy and loop_count < 60:
            while op_busy:
                response = cfn.describe_stack_set_operation(
                    StackSetName=stack_name,
                    OperationId=op_id
                )
                if response['StackSetOperation']['Status'] in inprogress_status:
                    print(f"StackSet Id: {response['StackSetOperation']['OperationId']} still running, have been waiting for {(loop_count*15)}s")
                    loop_count += 1
                    time.sleep(15)
                else:
                    op_busy = False
        return
    def stack_set_waiter(self, session, stack_set_name):
        cfn = session.client('cloudformation')
        # DEBUG
        #inprogress_operations.append({'OperationId': 'eb2b441e-564f-11e9-b959-0242ac110002', 'Action': 'CREATE', 'Status': 'RUNNING'})
        # DEBUG
        # print("IN PROGRESS OPERATIONS:")
        # print(inprogress_operations)
        # print(f"LENGTH OF OPS ARRAY: {len(inprogress_operations)}")
        inprogress_status = ['RUNNING', 'STOPPING']
        # TODO decide whether or not ot pass in stack operation
        inprogress_operations = self.get_stack_set_operations(cfn, stack_set_name, inprogress_status)
        if len(inprogress_operations) == 0:
            poll_count = 0
            while len(inprogress_operations) < 1 and poll_count <= 6:
                poll_count += 1 #increment loop count
                time.sleep(5) #sleep for 5 seconds
                inprogress_operations = self.get_stack_set_operations(cfn, stack_set_name, inprogress_status) # populate again

            if len(inprogress_operations) == 0: # Are you SURE there are no stack set operations running
                return "No StackSets to wait on"
            else:
                print(f"STACK SET API RETURNED 0, WAITED {(5*poll_count)}s, NOW THERE IS AN OPERATION!!")
        for operation in inprogress_operations:
            running = True
            counter = 0
            while running:
                response = cfn.describe_stack_set_operation(
                    StackSetName=stack_set_name,
                    OperationId=operation['OperationId']
                )
                # DEBUG
                # response['StackSetOperation']['Status'] = 'RUNNING'
                if response['StackSetOperation']['Status'] in inprogress_status:
                    print(f"StackSet Id: {response['StackSetOperation']['OperationId']} still running, , have been waiting for {(counter*15)}s")

                    counter += 1
                    if counter > 60:
                        raise RuntimeError(f"{response['StackSetOperation']['OperationId']} took too long")
                    time.sleep(15)

                else:
                    running = False
            print(f"{operation['OperationId']} No Longer Running")

        #'Status': 'RUNNING' | 'SUCCEEDED' | 'FAILED' | 'STOPPING' | 'STOPPED',
        return