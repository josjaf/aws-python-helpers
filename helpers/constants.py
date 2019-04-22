class Constants():
    def __init__(self, *args, **kwargs):
        return
    accounts_list = {
        '12345-artifact-pipeline': {
            'account_id': '12345',
            'profile': 'aws2',
            'region': 'us-east-1',
            'env_file': f'conf/12345-artifact-pipeline.env',
            'config_file': 'artifact_pipeline.yml'
        },
        '12345-security-app-pipeline': {
            'account_id': '12345',
            'profile': 'aws2',
            'region': 'us-east-1',
            'env_file': f'conf/12345-security-app-pipeline.env',
            'config_file': 'security_app_pipeline.yml'
        },
        '12345-artifact-pipeline': {
            'account_id': '12345',
            'profile': 'shared',
            'region': 'us-east-1',
            'env_file': f'conf/12345-artifact-pipeline.env',
            'config_file': 'artifact_pipeline.yml'
        },
        '12345-security-app-pipeline': {
            'account_id': '12345',
            'profile': 'shared',
            'region': 'us-east-1',
            'env_file': f'conf/12345-security-app-pipeline.env',
            'config_file': 'security_app_pipeline.yml'
        }
    }