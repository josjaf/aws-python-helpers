import re

import boto3

from . import log_helpers

logger = log_helpers.get_logger()


def get_iam_roles(session):
    iam = session.client('iam')
    paginator = iam.get_paginator('list_roles')
    page_iterator = paginator.paginate()
    iam_roles = []
    for page in page_iterator:
        for role in page['Roles']:
            iam_roles.append(role['RoleName'])
    return iam_roles


def check_iam_role_exists(session, role):
    iam_roles = get_iam_roles(session)
    if role in iam_roles:
        return True
    else:
        return False


def split_role_arn(arn):
    account_id = arn.split(":")[4]
    role_name = re.sub(r"^role/", "/", arn.split(":")[5], 1)
    return account_id, role_name


def sts_to_iam_arn(session):
    sts = session.client('sts')
    response_arn = sts.get_caller_identity()['Arn']
    # TODO FIX blank

    if ':user/' not in response_arn:
        if 'assumed-role' in response_arn:  # might mean there is a session
            response_arn = response_arn.replace("arn:aws:sts", "arn:aws:iam")
            response_arn = response_arn.replace("assumed-role", "role")
            constructed_arn = response_arn.rsplit("/", 1)[0]
        return constructed_arn
    else:
        return response_arn


def delete_old_access_key(session, user):
    """
    delete the oldest access key for an iam user
    :param session:
    :param user:
    :return:
    """
    iam = session.client('iam')
    logger.info(f"Found 2 Keys")

    keylist = iam.list_access_keys(UserName=user)['AccessKeyMetadata']
    keylist = sorted(keylist, key=lambda i: i['CreateDate'])
    oldest_key = keylist[0]['AccessKeyId']
    logger.critical(f"Deleting Oldest Access Key:{oldest_key}")
    response = iam.delete_access_key(
        UserName=user,
        AccessKeyId=oldest_key
    )

    return


def delete_access_keys(session, user):
    iam = session.client('iam')
    try:
        keylist = iam.list_access_keys(UserName=user)['AccessKeyMetadata']
        logger.info(f"Key List:{keylist}")
        for ak in keylist:
            response = iam.delete_access_key(
                UserName=user,
                AccessKeyId=ak['AccessKeyId']
            )
            logger.info(f"Deleting Key: {ak['AccessKeyId']}")
        return keylist
    except:
        pass
    return


if __name__ == '__main__':
    print(f"Log Level: {logger.level}")
    logger.info("INFO")
    session = boto3.session.Session()
