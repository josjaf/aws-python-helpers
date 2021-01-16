from botocore.config import Config

botocore_client_config = Config(
    retries=dict(
        max_attempts=10
    ),
    parameter_validation=True,
)
