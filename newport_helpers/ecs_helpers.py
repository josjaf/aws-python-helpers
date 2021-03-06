import botocore

from . import log_helpers

logger = log_helpers.get_logger()


def get_ecs_services(session):
    """

    :param session:
    :return:
    """
    ecs = session.client('ecs')

    paginator = ecs.get_paginator('list_clusters')
    response_iterator = paginator.paginate()
    #
    clusters = []
    for page in response_iterator:
        for cluster in page['clusterArns']:
            clusters.append(cluster)

    services = []
    for cluster in clusters:
        response = ecs.list_services(
            cluster=cluster,
            # nextToken='string',
            # maxResults=123,
            # launchType='EC2'|'FARGATE',
            # schedulingStrategy='REPLICA'|'DAEMON'
        )
        ### handle clusters with no services
        try:
            service_response = ecs.describe_services(
                cluster=cluster,
                services=response['serviceArns']
            )
            for service in service_response['services']:
                services.append(service)


        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'InvalidParameterException':
                continue
        except Exception as e:
            raise e

    logger.info(f"Total ECS Servics Count: {len(services)}")
    return services


def get_log_group_from_services(session, services):
    """

    :param session:
    :param services:
    :return:
    """
    log_groups = []
    ecs = session.client('ecs')
    for service in services:
        task_definition = service['taskDefinition']
        task_definition = ecs.describe_task_definition(
            taskDefinition=task_definition,
        )['taskDefinition']
        for container_definition in task_definition['containerDefinitions']:
            if 'logConfiguration' in container_definition:
                if container_definition['logConfiguration']['logDriver'] == 'awslogs':
                    log_group = container_definition['logConfiguration']['options']['awslogs-group']
                    try:
                        result = dict(LogGroup=log_group, TaskDefinition=task_definition['taskDefinitionArn'],
                                      Service=service, Role=task_definition['executionRoleArn'])
                        log_groups.append(result)
                    except KeyError:
                        logger.info(f"No Execution Role Arn for Service: {service['serviceArn']}")
                        continue
                    except Exception as e:
                        raise e

    return log_groups
