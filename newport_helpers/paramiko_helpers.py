import time
import newport_helpers
import paramiko
from newport_helpers import network_helpers, helpers

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


def paramiko_ssh_password(hostname, user, password, logger, port=22):
    """
    return a paramiko client using ssh username and password
    :param hostname:
    :param user:
    :param password:
    :param logger:
    :param port:
    :return:
    """

    username = user
    password = password

    # logger.info("Username {}, SSH-Config: {}".format(username, ssh_config))
    response = network_helpers.is_connected(hostname, 22)
    logger.info(f"SSH: {hostname}, username: {username}")
    try:
        c = paramiko.SSHClient()
        # do not load system host keys because we are running from a container
        # c.load_system_host_keys()
        c.set_missing_host_key_policy(paramiko.WarningPolicy)
        c.connect(hostname=hostname, username=username,
                  password=password, port=port)
        # stdin, stdout, stderr = c.exec_command('ls -lha')
        # logger.info()
        # stdout.read()
    except paramiko.ssh_exception.AuthenticationException:
        logger.error("SSH Authentication Failed! Bad Password")
    # finally:
    #    client.close()

    return c

def paramiko_ssh_from_key(hostname, username, private_key_path, logger):
    """
    return a paramiko client using a private key
    :param hostname:
    :param username:
    :param private_key_path:
    :param logger:
    :return:
    """

    response = network_helpers.is_connected(hostname, 22)
    logger.info("TCP is connected: {}".format(response))
    private_key_str = helpers.file_to_string(private_key_path)
    k = paramiko.RSAKey.from_private_key(StringIO(private_key_str))

    logger.info("DEBUG STATEMENT")

    c = paramiko.SSHClient()
    # c.load_system_host_keys()
    c.set_missing_host_key_policy(paramiko.WarningPolicy)
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # logger.info("Connecting to %s (%s)", csr_name, ssh_config['ip'])
    stime = time.time()
    try:
        c.connect(hostname=hostname, username=username, pkey=k)
        # PubKeyAuth=True
    except paramiko.ssh_exception.AuthenticationException:
        logger.error("PubKey Authentication Failed! Connecting with password")
        # PubKeyAuth = False

        # c.connect( hostname = csr_ip, username = config['USER_NAME'], password = config['PASSWORD'] )

    # except Exception as e:
    #     raise Exception(e)

    return c

