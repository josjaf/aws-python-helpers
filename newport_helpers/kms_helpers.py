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
        if not alias.startswith('alias/'):
            print("alias must start with alias/")
        kms_client = session.client('kms')
        kms_response = kms_client.describe_key(KeyId=alias)
        return kms_response['KeyMetadata']['KeyId']

    def list_grants_paginate(self, session, key_id):
        grants_list = []
        kms_client = session.client('kms')
        paginator = kms_client.get_paginator('list_grants')
        response_iterator = paginator.paginate(KeyId=key_id)
        for page in response_iterator:
            for item in page.get('Grants'):
                grants_list.append(item)
        return grants_list

    def revoke_grants_by_name(self, session, key_id, grant_friendly_id):
        kms_client = session.client('kms')
        grants_list = self.list_grants_paginate(session, key_id)
        response = None
        for grant in grants_list:
            if grant['Name'] == grant_friendly_id:
                response = kms_client.revoke_grant(
                    KeyId=grant['KeyId'],
                    GrantId=grant['GrantId']
                )
        return response

    def create_idempontent_grant(self, session, grant_friendly_id, grantee_arn, alias):
        kms_client = session.client('kms')
        kms_response = kms_client.describe_key(KeyId=f"alias/{alias}")
        key_id = kms_response['KeyMetadata']['Arn']
        grants_list = self.list_grants_paginate(session, key_id)
        response = self.revoke_grants_by_name(session, key_id, grant_friendly_id)

        response = kms_client.create_grant(
            KeyId=key_id,
            GranteePrincipal=grantee_arn,
            # RetiringPrincipal='string',
            Operations=['Decrypt', 'Encrypt', 'GenerateDataKey'],
            Name=grant_friendly_id
        )
        return response
