import time
def directory_service_replication_waiter(session, directory_id, replication_region):
    ds = session.client('ds')
    # 'Requested'|'Creating'|'Created'|'Active'|'Inoperable'|'Impaired'|'Restoring'|'RestoreFailed'|'Deleting'|'Deleted'|'Failed',
    directoryFinished = False
    counter = 0
    sleep = 30
    counter = 0
    ssm = session.client('ssm')
    finished_status = ['Active', 'Created']
    failed_status = ['Impaired', 'Deleting', 'Inoperable', 'Failed']
    running_status = ['Requested', 'Creating', 'Restoring']
    running = True
    print(f"Running Directory Service Replication waiter")
    while running:
        time.sleep(30) # give the api time to register the command to avoid throwing an exception
        counter += 1
        response = ds.describe_regions(
            DirectoryId=directory_id,
            RegionName=replication_region,
        )
        print(response)
        if response['RegionsDescription'][0]['Status'] in finished_status:
            running = False
        if response['RegionsDescription'][0]['Status'] in running_status:
            running = True

        if response['RegionsDescription'][0]['Status'] in failed_status:
            raise Exception(f"Failed Status: {response['RegionsDescription'][0]['Status']}")

        time.sleep(10)
    status = response['RegionsDescription'][0]['Status']
    return status