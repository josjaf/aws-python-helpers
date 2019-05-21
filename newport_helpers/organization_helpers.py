import boto3
from newport_helpers import helpers

Helpers = helpers.Helpers()


class Organization_Helpers():
    def get_org_accounts(self, session, remove_org_master=True):
        """
        return a list of all accounts in the organization
        :param session:
        :return:
        """
        org_master_account_id = session.client('sts').get_caller_identity()['Account']
        org_client = session.client('organizations')
        account_ids = []
        response = org_client.list_accounts()
        for account in response['Accounts']:
            account_ids.append(account['Id'])
        while 'NextToken' in response:
            response = org_client.list_accounts(NextToken=response['NextToken'])
            for account in response['Accounts']:
                account_ids.append(account['Id'])

        if remove_org_master:
            account_ids.remove(org_master_account_id)
        return account_ids
    def get_account_email_from_organizations(self, org_session, account_id):
        """
        pass in org session and account id and return the email associated with the account
        :param org_session:
        :param account_id:
        :return:
        """
        org_client = org_session.client('organizations')
        response = org_client.list_accounts()

        if account_id not in [a['Id'] for a in response['Accounts']]:
            print(f"Account ID: {account_id} not found in Organization")
            return False
        account_id_dict = [a for a in response['Accounts'] if a['Id'] == account_id]
        account_email = account_id_dict[0]['Email']
        return account_email

    def org_loop_entry(self, org_profile=None, account_role=None):
        """
        returns a generator for an account loop that takes an org profile and account role in for operational parameters
        :param org_profile:
        :param account_role:
        :return:
        """
        session_args = {}
        if org_profile:
            session_args['profile_name'] = org_profile
        if not account_role:
            account_role = 'OrganizationAccountAccessRole'
        session = boto3.session.Session(**session_args)
        for account in self.get_org_accounts(session):
            session = Helpers.get_child_session(account, account_role, None)
            yield account, session

