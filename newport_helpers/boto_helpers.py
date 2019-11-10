from botocore.config import Config
class BotoHelpers():
    def __init__(self, *args, **kwargs):
        return
    botocore_client_config = Config(
        retries=dict(
            max_attempts=10
        ),
        parameter_validation=True,
    )