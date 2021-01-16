from newport_helpers import helpers, docker_helpers, cfn_helpers, iam_helpers, org_helpers, codebuild_helpers, \
    aws_credential_helpers


class NPH():
    """
    Super class for importing
    """

    def __init__(*args, **kwargs):
        return

    Helpers = helpers
    Docker_Helpers = docker_helpers
    Cfn_Helpers = cfn_helpers
    Iam_Helpers = iam_helpers
    Org_Helpers = org_helpers
    CodeBuild_Helpers = codebuild_helpers
    AWSCredentialHelpers = aws_credential_helpers