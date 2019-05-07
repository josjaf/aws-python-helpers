from stacker.blueprints.base import Blueprint
from troposphere.sns import SubscriptionResource, Topic


class SNSEmailSubscriptions(Blueprint):
    """
    Manages the creation of SNS email subscriptions.
    """

    VARIABLES = {
        "TopicArn": {
            "type": str,
            "description": "Dictionary of SNS Topic definitions",
        },
        "Emails": {
            "type": list,
            "description": "Dictionary of SNS Topic definitions",
        }
    }

    def create_subscriptions(self):
        variables = self.get_variables()
        self.template.description = ("variable length sns subscriptions")
        counter = 0
        for email in variables['Emails']:
            resource_title = f"subscription{counter}"
            self.template.add_resource(SubscriptionResource(
                resource_title,
                Endpoint=email,
                Protocol='email',
                TopicArn=variables['TopicArn']

            ))
            counter += 1

    def create_template(self):
        self.create_subscriptions()
