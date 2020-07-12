import boto3
import botocore


class ServiceCatalogHelpers():

    def get_provisioning_artifact_id(self, session, prod_id):
        ''' Query for Provisioned Artifact Id '''

        pa_list = list()
        service_catalog = session.client('servicecatalog')
        try:
            pa_list = service_catalog.describe_product_as_admin(Id=prod_id)['ProvisioningArtifactSummaries']
        except Exception as exe:
            raise RuntimeError("Unable to find the Provisioned Artifact Id: " + str(exe))

        if len(pa_list) > 0:
            output = pa_list[-1]['Id']
        else:
            raise RuntimeError("Unable to find the Provisioned Artifact Id: " + str(pa_list))

        return output

    def get_launch_path(self, session, prod_id):
        service_catalog = session.client('servicecatalog')
        try:
            response = service_catalog.list_launch_paths(
                ProductId=prod_id)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print("Launch Path not found")
        return response