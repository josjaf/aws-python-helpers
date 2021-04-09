import newport_helpers

logger = newport_helpers.nph.logger

def get_latest_ami_by_tag(session, tag):
    """
    latest image by ec2 tag
    :param session:
    :param tag:
    :return:
    """
    ec2 = session.client('ec2')
    response = ec2.describe_images(

        Filters=[
            {
                'Name': 'tag:AppName',
                'Values': [
                    tag,
                ]
            },
        ],

        Owners=[
            'self',
        ],
    )
    images = sorted(response['Images'], key=lambda i: i['CreationDate'], reverse=True)
    latest_image = images[0]['ImageId']
    return latest_image, images

def get_endpoint_service_az(session, service_name):
    """
    get the azs for a specific service
    :param session:
    :param service_name:
    :return:
    """
    ec2 = session.client('ec2')
    region = session.region_name
    dns_service_name = f'com.amazonaws.{region}.{service_name}'
    response = ec2.describe_vpc_endpoint_services(ServiceNames=[dns_service_name])
    logger.info(response)

    # get the dictionary for the endpoint we are looking for
    endpoint_config = \
        [d for d in response['ServiceDetails'] if dns_service_name in d['ServiceName']][0]
    availability_zones = sorted(endpoint_config['AvailabilityZones'])

    return availability_zones


def get_vpcs_all_regions(session):
    """
    Get all of the vpcs in an account
    :param session:
    :return:
    """
    vpcs = []
    ec2 = session.client('ec2')
    response = ec2.describe_regions()
    for region in response['Regions']:
        ec2 = session.client('ec2', region_name=region['RegionName'])
        response = ec2.describe_vpcs()
        for vpc in response['Vpcs']:
            vpc['Region'] = region['RegionName']
            # print(f"Region: {region['RegionName']}, VPC:{vpc['VpcId']}")
            vpcs.append(vpc)
    return vpcs


def route_table_public_private(session):
    """
    Determine wheter a route table has a route to an igw
    :param session:
    :return:
    """
    processed_route_tables = []
    ec2 = session.client('ec2')
    response = ec2.describe_route_tables()
    for rt in response['RouteTables']:
        for route in rt['Routes']:
            print(route)
            rt['Public'] = False
            if route.get('DestinationCidrBlock') == '0.0.0.0/0' and route.get('GatewayId') and route.get(
                    'GatewayId').startswith('igw'):
                print(f"FOUND IGW  on RT: {rt['RouteTableId']}")
                rt['Public'] = True
                break

        processed_route_tables.append(rt)



