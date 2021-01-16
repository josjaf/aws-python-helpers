import time


def codebuild_job_waiter(session, buildId):
    """
    wait for a codebuild job to complete
    :param session:
    :param buildId:
    :return:
    """
    cb = session.client('codebuild')
    buildSucceeded = False
    counter = 0
    sleep = 15
    print(f"CodeBuild BuildId: {buildId} waiting activated")
    while counter < 10:  # capped this, so it just fails if it takes too long
        time.sleep(sleep)

        counter = counter + 1
        theBuild = cb.batch_get_builds(ids=[buildId])
        buildStatus = theBuild['builds'][0]['buildStatus']
        print(f"CodeBuild BuildId: {buildId} waiting for {counter * sleep}")

        if buildStatus == 'SUCCEEDED':
            buildSucceeded = True
            print(f"CodeBuild BuildId: {buildId} status: {buildStatus}")
            break
        elif buildStatus == 'FAILED' or buildStatus == 'FAULT' or buildStatus == 'STOPPED' or buildStatus == 'TIMED_OUT':
            print(f"CodeBuild BuildId: {buildId} status: {buildStatus}")
            break
    return buildStatus
