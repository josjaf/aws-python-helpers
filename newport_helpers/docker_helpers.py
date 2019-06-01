import datetime
import git
import docker


class DockerHelpers():
    def __init__(self, *args, **kwargs):
        return

    def docker_build_image(self, tag, docker_file, labels):
        docker_client = docker.from_env()

        t = datetime.datetime.now()
        print("Rebuilding the Container")
        repo = git.Repo(search_parent_directories=True)
        sha = repo.head.object.hexsha

        # TODO add exception processing for requests.exceptions.ConnectionError when docker dameon is not running
        buildtime = t.strftime("%m-%d-%Y %H:%M:%S")

        response = docker_client.images.build(path='.', tag=tag, labels=labels, dockerfile=docker_file)
        container_build_time = datetime.datetime.now() - t
        print(f"Rebuilding the container took: {container_build_time}")
        print("$ docker run example")

        return
