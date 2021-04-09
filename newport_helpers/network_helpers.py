import socket
import newport_helpers
logger = newport_helpers.nph.logger

def is_connected(hostname, port):
    try:
        socket.setdefaulttimeout(5)
        host = socket.gethostbyname(hostname)
        s = socket.create_connection((host, port), 2)
        s.close()
        logger.info(f"Connected to {hostname} on {port}")
        return True

    except Exception as e:
        print(e)
        # print "internet off."
    return False