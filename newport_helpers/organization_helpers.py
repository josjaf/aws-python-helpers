import boto3
from newport_helpers import helpers

Helpers = helpers.Helpers()


class Organization_Helpers():

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
        for account in Helpers.get_org_accounts(session):
            session = Helpers.get_child_session(account, account_role, None)
            yield account, session
