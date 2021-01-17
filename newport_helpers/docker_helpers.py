import datetime
from base64 import b64decode

import docker
import requests

from newport_helpers import log_helpers
import boto3
logger = log_helpers.get_logger()


def docker_running_check(docker_client):
    """
    ensure that the docker engine is running. this method avoids harder exceptions
    to debug that come from the docker engine not running, like file not found error
    :param docker_client:
    :return:
    """
    try:
        docker_client.containers.list()
        logger.info('Docker Client Running')
    except requests.exceptions.ConnectionError as e:
        logger.error("Ensure that Docker Daemon is running")
        logger.error(
            "Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?")
        raise RuntimeWarning
    except Exception as e:
        logger.error(type(e))
        logger.error(e)

    return


def docker_build_image(tag, docker_file, labels, path='.'):
    # TODO Determine whether change directory is required to the same dir as the dockerfile
    """
    build docker image locally
    :param tag:
    :param docker_file:
    :param labels:
    :return:
    """
    docker_client = docker.from_env()
    docker_running_check(docker_client)
    t = datetime.datetime.now()
    logger.info("Rebuilding the Container")

    # TODO add exception processing for requests.exceptions.ConnectionError when docker dameon is not running
    buildtime = t.strftime("%m-%d-%Y %H:%M:%S")
    # build returns tuple, with image object and build logs
    try:
        response = docker_client.images.build(path=path, tag=tag, labels=labels, dockerfile=docker_file)
        for line in response[1]:
            logger.info(line)

    except Exception as e:
        logger.error(e)
        raise e
    container_build_time = datetime.datetime.now() - t
    logger.info(f"Rebuilding the container took: {container_build_time}")
    logger.info("$ docker run example")

    return

def ecr_login(session, ecr_name):
    region = session.region_name
    identity = session.client("sts").get_caller_identity()
    account_id = identity['Account']
    registry = f"{account_id}.dkr.ecr.{region}.amazonaws.com/{ecr_name}"

    # tag image
    docker_client = docker.from_env()
    docker_running_check(docker_client)
    logger.info(f'Logging into AWS ECR: {registry}')
    ecr = session.client('ecr', region_name=session.region_name)
    login_response = ecr.get_authorization_token()
    token = b64decode(login_response['authorizationData'][0]['authorizationToken']).decode()
    username, password = token.split(':', 1)
    registry = login_response['authorizationData'][0]['proxyEndpoint']
    response = docker_client.login(username=username, password=password, registry=registry, reauth=True, email=None)
    return response, username, password, registry

def ecr_push(session, tag, ecr_name):
    """
    push local docker imagae to ecr
    :param session:
    :param tag:
    :param ecr_name:
    :return:
    """
    region = session.region_name
    identity = session.client("sts").get_caller_identity()
    account_id = identity['Account']
    registry = f"{account_id}.dkr.ecr.{region}.amazonaws.com/{ecr_name}"

    # tag image
    docker_client = docker.from_env()
    docker_running_check(docker_client)
    image = docker_client.images.get(f'{tag}:latest')
    image.tag(registry, tag)

    # login
    ecr = session.client('ecr', region_name=session.region_name)
    login_response = ecr.get_authorization_token()
    token = b64decode(login_response['authorizationData'][0]['authorizationToken']).decode()
    username, password = token.split(':', 1)
    registry = login_response['authorizationData'][0]['proxyEndpoint']
    response = docker_client.login(username=username, password=password, registry=registry, reauth=True, email=None)
    logger.info(response)
    # changing latest to docker
    for line in docker_client.images.push(registry, tag=tag, stream=True, decode=True,
                                          auth_config=dict(username=username, password=password)):
        logger.info(line)

    logger.info(response)
    return


def run_docker(environment_variables, image_name, container_name, command=None):
    docker_client = docker.from_env()
    docker_running_check(docker_client)
    try:
        container = docker_client.containers.get(container_id=container_name)
        container.remove()
    except docker.errors.NotFound:
        pass
    except Exception as e:
        logger.info(e)
        raise e

    logger.info(f"Creating Docker Container {container_name} from image: {image_name}")
    # mounts = {os.getcwd(): {'bind': '/trident', 'mode': 'rw'}}

    environment_variables = environment_variables
    logger.info(f"env: {environment_variables}")
    docker_client.containers.run("example", command=command, detach=True,
                                 environment=environment_variables,
                                 name=container_name,
                                 log_config={"type": "json-file",
                                             "config": {"max-size": "1m"}}

                                 )
    logger.info(f"docker logs -f {container_name}")

    return
