import csv
import os
import threading
import uuid
import zipfile
import boto3
import botocore
import re
import boto3


class AutoScalingHelpers():
    def __init__(self, *args, **kwargs):
        return

    def asg_hooks_present(self, session, asg_group_name):
        """
        determine whether an autoscaling group has lifecycle hooks
        :param session:
        :param asg_id:
        :return:
        """
        autoscaling = session.client('autoscaling')
        response = autoscaling.describe_lifecycle_hooks(AutoScalingGroupName=asg_group_name)
        if not response['LifecycleHooks']:
            print(f"AutoScalingGroup: {asg_group_name} has NO lifecycle hooks")
            return False

        else:
            print(f"AutoScalingGroup: {asg_group_name} HAS lifecycle hooks")
            return True
