def paginator_generic(session, service, paginator_action, list_key):
    """

    this is a generic paginator
    results = paginator_generic(session, 'secretsmanager', 'list_secrets', 'SecretList')
    :param session:
    :param service:
    :param paginator_action:
    :param list_key:
    :return:
    """
    client = session.client(service)
    paginator = client.get_paginator(paginator_action)
    page_iterator = paginator.paginate()
    results = []
    for page in page_iterator:
        for item in page[list_key]:
            results.append(item)
    return results