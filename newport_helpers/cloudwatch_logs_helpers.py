import os

import time
from newport_helpers import log_helpers
logger = log_helpers.get_logger()

def logs_get_sequence_number(session, log_group, log_stream):
    logs = session.client('logs')
    os.environ.pop('uploadSequenceToken', None)

    response = logs.describe_log_streams(logGroupName=log_group)  # logStreamNamePrefix=log_stream)
    log_streams = [lg['logStreamName'] for lg in response['logStreams'] if lg['logStreamName'] == log_stream]
    if log_stream not in log_streams:
        logger.info("Log Stream does not currently exist")
        response = logs.create_log_stream(
            logGroupName=log_group,
            logStreamName=log_stream
        )
        # os.environ.pop('uploadSequenceToken')
        # no need to make any api calls here, there's no tokens on new streams
        return

    log_stream_data = [lg for lg in response['logStreams'] if lg['logStreamName'] == log_stream][0]
    logger.debug(f"Log Stream Data: {log_stream_data}")
    if 'uploadSequenceToken' not in log_stream_data.keys():
        logger.info("Found stream without SequenceToken you are probably manually testing. ")
        return

    os.environ['uploadSequenceToken'] = log_stream_data['uploadSequenceToken']
    logger.info(f"Using token {log_stream_data['uploadSequenceToken']}")
    return log_stream_data['uploadSequenceToken']


def logs_put_message(session, log_group, log_stream, message):
    logs = session.client('logs')
    kwargs = dict(
        logGroupName=log_group,
        logStreamName=log_stream,
        logEvents=[
            {
                'timestamp': int(round(time.time() * 1000)),
                'message': message
            },
        ]
    )
    if os.environ.get('uploadSequenceToken'):
        kwargs['sequenceToken'] = os.environ['uploadSequenceToken']
    logger.info(kwargs)
    response = logs.put_log_events(**kwargs)
    logger.info(response)
    if 'nextSequenceToken' in response:
        os.environ['uploadSequenceToken'] = response['nextSequenceToken']

    return response
