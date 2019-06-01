from newport_helpers import helpers, docker_helpers, cfn_helpers, iam_helpers, org_helpers


class Super():
    def __init__(self, *args, **kwargs):
        return

    Helpers = helpers.Helpers()
    Docker_Helpers = docker_helpers.DockerHelpers()
    Cfn_Helpers = cfn_helpers.CfnHelpers()
    Iam_Helpers = iam_helpers.IamHelpers()
    Org_Helpers = org_helpers.Organization_Helpers()
