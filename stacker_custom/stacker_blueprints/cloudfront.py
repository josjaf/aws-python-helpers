from stacker.blueprints.base import Blueprint
from troposphere import GetAtt, Join, Output
from troposphere import Parameter, Ref, Template
from troposphere.cloudfront import Distribution, DistributionConfig
from troposphere.cloudfront import Origin, DefaultCacheBehavior
from troposphere.cloudfront import ForwardedValues
from troposphere.cloudfront import S3OriginConfig
from troposphere.cloudfront import ViewerCertificate

class CloudFrontDistributionS3(Blueprint):
    """
    Manages the creation of SNS email subscriptions.
    """

    VARIABLES = {
        "Aliases": {
            "type": list,
            "description": "SNS Topic Arn",
        },
        "CfOriginAccessIdentity": {
            "type": str,
            "description": "List of emails to create individual objects for",
        },
        "s3dnsname": {
            "type": str,
            "description": "DNS Name for S3 Bucket",
        },
        "CertificateArn": {
            "type": str,
            "description": "DNS Name for S3 Bucket",
        }
    }

    def create_cloudfront(self):
        variables = self.get_variables()
        self.template.description = ("Newport Cloudfront BluePrint")
        #
        # s3dnsname = self.template.add_parameter(Parameter(
        #     "S3DNSName",
        #     Description="The DNS name of an existing S3 bucket to use as the "
        #                 "Cloudfront distribution origin",
        #     Type="String",
        # ))


        dist = Distribution(
            "myDistribution",
            DistributionConfig=DistributionConfig(
                Origins=[Origin(Id="Origin 1", DomainName=variables['s3dnsname'],
                                S3OriginConfig=S3OriginConfig(
                                    OriginAccessIdentity=f'origin-access-identity/cloudfront/{variables["CfOriginAccessIdentity"]}'))],
                DefaultCacheBehavior=DefaultCacheBehavior(
                    TargetOriginId="Origin 1",
                    AllowedMethods=['HEAD', 'GET'],
                    CachedMethods=['HEAD', 'GET'],
                    ForwardedValues=ForwardedValues(
                        QueryString=False
                    ),
                    ViewerProtocolPolicy="allow-all"),
                Enabled=True,
                HttpVersion='http1.1',
                PriceClass='PriceClass_100',
                DefaultRootObject='index.html',
                IPV6Enabled=False

            )
        )
        # aliases has to have certificates
        if 'Aliases' in variables:
            dist.properties['DistributionConfig'].properties['Aliases'] = variables['Aliases']
        if 'CertificateArn' in variables:
            dist.properties['DistributionConfig'].properties['ViewerCertificate'] = ViewerCertificate(AcmCertificateArn=variables['CertificateArn'],                         SslSupportMethod='sni-only')

        myDistribution = self.template.add_resource(dist)

        self.template.add_output([
            Output("DistributionId", Value=Ref(myDistribution)),
            Output(
                "DistributionName",
                Value=Join("", ["http://", GetAtt(myDistribution, "DomainName")])),
        ])


    def create_template(self):
        self.create_cloudfront()

