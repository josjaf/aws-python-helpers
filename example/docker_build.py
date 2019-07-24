"""
post_build:
  push_image:
    path: stacker_custom.hooks.post.docker_build_push.handler
    required: true
    args:
      ecrid: ecr::ecrid
      dockerfile: Dockerfile
      path: app_pipeline
      docker_tag: ${docker_stack_set_tag}

"""
import logging

from stacker.lookups.handlers.output import OutputLookup
from stacker.lookups.handlers.rxref import RxrefLookup
from stacker.lookups.handlers.xref import XrefLookup
from stacker.session_cache import get_session
from stacker.logger import setup_logging
from botocore.exceptions import ClientError

import boto3
import docker
import datetime
import git
from base64 import b64decode
import newport_helpers

NPH = newport_helpers.NPH()

logger = logging.getLogger(__name__)


def main():
    session = boto3.session.Session()
    handler = OutputLookup.handle
    ecr_name = 'josjaffe'

    t = datetime.datetime.now()
    buildtime = t.strftime("%m-%d-%Y %H:%M:%S")

    #labels = {'commit': sha, 'buildtime': buildtime}
    # making labels blank to prevent many iterations of the same container with different labaels
    labels = {}
    path = '.'
    tag = 'newport-helpers'
    docker_file = 'Dockerfile'
    build_kwargs = dict(tag=tag, docker_file=docker_file, labels=labels, path=path)


    NPH.Docker_Helpers.docker_build_image(**build_kwargs)
    NPH.Docker_Helpers.ecr_push(session=session, tag=tag, ecr_name=ecr_name)

    return labels


if __name__ == '__main__':
    main()
