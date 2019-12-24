import boto3
from newport_helpers import helpers
import threading
from botocore.exceptions import ClientError
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

    def get_principal_org_id(self, session):
        try:
            organizations = session.client('organizations')
            response = organizations.describe_organization()

            principal_org_id = response['Organization']['Id']

            params = {"PrincipalOrgID": principal_org_id}
            return principal_org_id

        except ClientError as e:
            if e.response['Error']['Code'] == 'AWSOrganizationsNotInUseException':
                print("#" * 75)
                raise RuntimeError("CREATE A NEW ORGANIZATION IN ACCOUNT OR JOIN TO CONTINUE")

        return

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

    def org_loop_entry_thread_worker(self, account, account_role, session, results):

        session = Helpers.get_child_session(account, account_role, session)
        response = (account, session)
        results.append(response)

    def org_loop_entry_thread(self, org_profile=None, account_role=None, remove_org_master=False):
        """
        returns a list of tuples with the account id and the child session
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
        threads = []
        results = []

        def worker(account, session, results):

            session = Helpers.get_child_session(account, account_role, None)
            response = (account, session)
            results.append(response)

        org_accounts = self.get_org_accounts(session, remove_org_master)
        print(len(org_accounts))
        for account in org_accounts:
            t = threading.Thread(target=self.org_loop_entry_thread_worker,
                                 args=(account, account_role, session, results))
            # t = threading.Thread(target=worker, args=(account, session, results))
            threads.append(t)
            print(f"Account {account}")
            t.start()

        print(len(threads))
        for thread in threads:
            thread.join()
        print(results)
        return results


if __name__ == '__main__':
    Organization_Helpers = Organization_Helpers()

    results = Organization_Helpers.org_loop_entry_thread()
    print(results)
