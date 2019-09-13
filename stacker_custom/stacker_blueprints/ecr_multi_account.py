"""
Create SNS Subscription for a give topic with a variable length of subscriptions to create, better than making api calls
"""
from stacker.blueprints.base import Blueprint
from troposphere.sns import SubscriptionResource, Topic
from troposphere.ecr import Repository, LifecyclePolicy
from awacs.aws import Allow, PolicyDocument, AWSPrincipal, Statement
import awacs.ecr as ecr
import awacs.iam as iam
from troposphere import Tags


class ECRMultiAccountTrust(Blueprint):
    """
    Manages the creation of SNS email subscriptions.
    """

    VARIABLES = {
        "namespace": {
            "type": str,
            "description": "SNS Topic Arn",
        },
        "Accounts": {
            "type": list,
            "description": "List of emails to create individual objects for",
        }
    }


    def create_repository(self):
        variables = self.get_variables()
        self.template.description = ("variable length ecr subscriptions")
        counter = 0

        arn_list = []
        # you can pass in a list of arns here instead of letting the troposphere objects construct them for you
        #f"arn:aws:iam::{account}:root"
        for account_id in variables['Accounts']:
            arn_list.append(iam.ARN(account=account_id, resource='root'))
        principals = AWSPrincipal(arn_list)
        resource_title = f"subscription{counter}"
        self.template.add_resource(Repository(
            f"ECRProd",
            #RepositoryName=f"{variables['namespace']}-ECR-Prod",
            # LifecyclePolicy=LifecyclePolicy(
            #     LifecyclePolicyText
            # ),
            RepositoryPolicyText=PolicyDocument(
                Version='2008-10-17',
                Statement=[
                    Statement(
                        Sid='AllowPull',
                        Effect=Allow,
                        Principal=principals,
                        Action=[
                            ecr.GetDownloadUrlForLayer,
                            ecr.BatchGetImage,
                            ecr.BatchCheckLayerAvailability,
                        ],
                    ),
                ]
            ),
            Tags=Tags(
                Name='namespace',
                Value=variables['namespace']

            )

        ))


    def create_template(self):
        self.create_repository()
