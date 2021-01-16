class StackSetConstants():
    def __init__(*args, **kwargs):
        return

    create_stack_set_args = dict(
        StackSetName='',
        Description='trident-test',
        TemplateBody='',
        # TemplateURL='string',
        # Parameters=[
        #     {
        #         'ParameterKey': 'SharedAccountId',
        #         'ParameterValue': org_master,
        #         'UsePreviousValue': False,
        #         # 'ResolvedValue': 'string'
        #     },
        # ],
        Capabilities=[
            'CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM', 'CAPABILITY_AUTO_EXPAND',
        ],
        Tags=[
            {
                'Key': 'App',
                'Value': 'newport'
            },
        ],
        # AdministrationRoleARN='string',
        ExecutionRoleName='AWSCloudFormationStackSetExecutionRole',
        # ClientRequestToken='string'
    )
    instaces_dict = dict(
        StackSetName='',
        Accounts=[],
        Regions=[
            'us-east-1',
        ],
        # ParameterOverrides=[
        #     {
        #         'ParameterKey': 'string',
        #         'ParameterValue': 'string',
        #         'UsePreviousValue': True | False,
        #         'ResolvedValue': 'string'
        #     },
        # ],
        OperationPreferences={
            'RegionOrder': [
                'us-east-1',
            ],
            # 'FailureToleranceCount': 123,
            'FailureTolerancePercentage': 25,
            # 'MaxConcurrentCount': 123,
            'MaxConcurrentPercentage': 100
        },
        OperationId=''
    )
