import os
import datetime
import git
import urllib3
import docker
import requests
from base64 import b64decode


class DockerHelpers():
    def __init__(self, *args, **kwargs):
        return

    def docker_running_check(self, docker_client):
        """
        ensure that the docker engine is running. this method avoids harder exceptions
        to debug that come from the docker engine not running, like file not found error
        :param docker_client:
        :return:
        """
        try:
            docker_client.containers.list()
        except requests.exceptions.ConnectionError as e:
            print("Ensure that Docker Daemon is running")
            print("Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?")
            raise RuntimeWarning
        except Exception as e:
            print(type(e))
            print(e)

        return
    def docker_build_image(self, tag, docker_file, labels, path='.'):
        #TODO Determine whether change directory is required to the same dir as the dockerfile
        """
        build docker image locally
        :param tag:
        :param docker_file:
        :param labels:
        :return:
        """
        docker_client = docker.from_env()
        self.docker_running_check(docker_client)
        t = datetime.datetime.now()
        print("Rebuilding the Container")
        repo = git.Repo(search_parent_directories=True)
        sha = repo.head.object.hexsha

        # TODO add exception processing for requests.exceptions.ConnectionError when docker dameon is not running
        buildtime = t.strftime("%m-%d-%Y %H:%M:%S")
        # build returns tuple, with image object and build logs
        try:
            response = docker_client.images.build(path=path, tag=tag, labels=labels, dockerfile=docker_file)
            for line in response[1]:
                print(line)

        except Exception as e:
            print(e)
        container_build_time = datetime.datetime.now() - t
        print(f"Rebuilding the container took: {container_build_time}")
        print("$ docker run example")

        return
    def ecr_push(self, session, tag, ecr_name):
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
        self.docker_running_check(docker_client)
        image = docker_client.images.get(f'{tag}:latest')
        image.tag(registry, tag)

        # login
        ecr = session.client('ecr', region_name=session.region_name)
        login_response = ecr.get_authorization_token()
        token = b64decode(login_response['authorizationData'][0]['authorizationToken']).decode()
        username, password = token.split(':', 1)
        print(username, password)
        print(f"UserName: {username}")
        print(f"Password: {password}")
        response = docker_client.login(username=username, password=password, registry=registry, reauth=True, email=None)
        print(response)
        # changing latest to docker
        for line in docker_client.images.push(registry, tag=tag,stream=True, decode=True,
                                              auth_config=dict(username=username, password=password)):
            print(line)

        print(response)
        return