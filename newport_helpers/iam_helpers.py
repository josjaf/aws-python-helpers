import re


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
