from stacker.hooks.aws_lambda import upload_lambda_functions


def custom_upload_lambda_functions(context, provider, **kwargs):
    new_results = {}
    results = upload_lambda_functions(context, provider, **kwargs)
    for name, code_obj in results.items():
        new_results = {
            "s3_key": code_obj.S3Key,
            "s3_bucket": code_obj.S3Bucket
        }
    return new_results
