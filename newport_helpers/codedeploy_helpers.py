import time
import newport_helpers
logger = newport_helpers.nph.logger

def codedeploy_waiter(session, deployment_id):
    code_deploy = session.client('codedeploy')
    # 'Created'|'Queued'|'InProgress'|'Baking'|'Succeeded'|'Failed'|'Stopped'|'Ready'
    status = 'WAITER'
    counter = 0
    sleep = 15
    completed_status = ['Succeeded', 'Failed', 'Stopped']
    logger.info(f"DeploymentId: {deployment_id} waiting activated")
    deploySucceeded = False  # get a false status when the timer runs out
    while counter <= 10:

        logger.info(f"Sleeping for 15, waiting for DeploymentId: {deployment_id}")
        time.sleep(sleep)
        response = code_deploy.get_deployment(
            deploymentId=deployment_id
        )
        # plogger.info.plogger.info(response)
        status = response['deploymentInfo']['status']
        counter += 1
        if status == 'Succeeded':
            deploySucceeded = True
            logger.info(f"CodeDeploy DeploymentId: {deployment_id} status: {deploySucceeded}")
            break
        if status == 'Failed' or status == 'Stopped':
            deploySucceeded = False
            logger.info(f"CodeDeploy DeploymentId: {deployment_id} status: FAILED OR STOPPED")
            break

    return deploySucceeded
