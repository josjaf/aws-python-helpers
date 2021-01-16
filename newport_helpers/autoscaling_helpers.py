import log_helpers
logger = log_helpers.get_logger()
def asg_hooks_present(session, asg_group_name: str):
    """
    determine whether an autoscaling group has lifecycle hooks
    :param session:
    :param asg_id:
    :return:
    """
    autoscaling = session.client('autoscaling')
    response = autoscaling.describe_lifecycle_hooks(AutoScalingGroupName=asg_group_name)
    if not response['LifecycleHooks']:
        logger.info(f"AutoScalingGroup: {asg_group_name} has NO lifecycle hooks")
        return False

    else:
        logger.info(f"AutoScalingGroup: {asg_group_name} HAS lifecycle hooks")
        return True


def get_asg_from_name(session, asg_group_name: str):
    """
    describe asg from name
    :param session:
    :param asg_group_name:
    :return:
    """
    asg = session.client('autoscaling')
    response = asg.describe_auto_scaling_groups()
    asg_response = [g for g in response['AutoScalingGroups'] if g['AutoScalingGroupName'] == asg_group_name][0]
    return asg_response
