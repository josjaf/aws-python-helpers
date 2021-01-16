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
    print(response)

    # get the dictionary for the endpoint we are looking for
    endpoint_config = \
        [d for d in response['ServiceDetails'] if dns_service_name in d['ServiceName']][0]
    availability_zones = sorted(endpoint_config['AvailabilityZones'])

    return availability_zones

# TODO
