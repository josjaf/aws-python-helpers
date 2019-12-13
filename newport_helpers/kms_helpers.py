import boto3 


class KMShelpers():

    def __init__(self, *args, **kwargs):
        return

    def _list_keys_raw(self, session):
        key_id_arr = []
        kms_client = session.client('kms')
        paginator = kms_client.get_paginator('list_keys')
        response_iterator = paginator.paginate()
        for page in response_iterator:
            for item in page.get('Keys'):
                key_id_arr.append(item)
        return key_id_arr

    def list_keys(self, session):
        key_ids = []
        keys = self._list_keys_raw(session)
        for key in keys:
            key_ids.append(key.get('KeyId'))
        return key_ids

    def _list_aliases_raw(self, session):
        key_alias_arr = []
        kms_client = session.client('kms')
        paginator = kms_client.get_paginator('list_aliases')
        response_iterator = paginator.paginate()
        for page in response_iterator:
            for item in page.get('Aliases'):
                key_alias_arr.append(item)
        return key_alias_arr

    def list_aliases(self, session):
        alias_names = []
        aliases = self._list_aliases_raw(session)
        for alias in aliases:
            alias_names.append(alias.get('AliasName'))
        return alias_names

    def describe_key_from_alias(self, session, alias):
        kms_client = session.client('kms')
        kms_response = kms_client.describe_key(KeyId=alias)
        return kms_response['KeyMetadata']['KeyId']


