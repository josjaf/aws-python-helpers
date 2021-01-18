import git
from newport_helpers import log_helpers
logger = log_helpers.get_logger()

def get_commit_sha(dir='.', repo_bare_exception=False):
    """

    :param dir:
    :param repo_bare_exception:
    :return:
    """
    repo = git.repo.Repo(dir)
    if repo.bare:
        commit = None

        if repo_bare_exception:
            # when i get a blank repo, and repo_bare_exception=True
            raise RuntimeError("Blank Git Repo")
        else:
            return commit

    commit = repo.head.commit.hexsh
    return commit
