class Constants():
    def __init__(self, *args, **kwargs):
        return
    accounts_list = {
        '253737654488-artifact-pipeline': {
            'account_id': '253737654488',
            'profile': 'aws2',
            'region': 'us-east-1',
            'env_file': f'conf/253737654488-artifact-pipeline.env',
            'config_file': 'artifact_pipeline.yml'
        },
        '253737654488-security-app-pipeline': {
            'account_id': '253737654488',
            'profile': 'aws2',
            'region': 'us-east-1',
            'env_file': f'conf/253737654488-security-app-pipeline.env',
            'config_file': 'security_app_pipeline.yml'
        },
        '774906637191-artifact-pipeline': {
            'account_id': '774906637191',
            'profile': 'shared',
            'region': 'us-east-1',
            'env_file': f'conf/774906637191-artifact-pipeline.env',
            'config_file': 'artifact_pipeline.yml'
        },
        '774906637191-security-app-pipeline': {
            'account_id': '774906637191',
            'profile': 'shared',
            'region': 'us-east-1',
            'env_file': f'conf/774906637191-security-app-pipeline.env',
            'config_file': 'security_app_pipeline.yml'
        }
    }