# get a common prefix
import os
from io import BytesIO
from zipfile import ZipFile
from newport_helpers import log_helpers
logger = log_helpers.get_logger()

def get_members(zip):
    """
    if the zip files have a prefix directory, this will remove it during extraction
    zip.extractall(p, get_members(zip))
    :param zip:
    :return:
    """
    parts = []
    # get all the path prefixes
    for name in zip.namelist():
        # only check files (not directories)
        if not name.endswith('/'):
            # keep list of path elements (minus filename)
            parts.append(name.split('/')[:-1])
    # now find the common path prefix (if any)
    prefix = os.path.commonprefix(parts)
    if prefix:
        # re-join the path elements
        prefix = '/'.join(prefix) + '/'
    # get the length of the common prefix
    offset = len(prefix)
    # now re-set the filenames
    for zipinfo in zip.infolist():
        name = zipinfo.filename
        # only check files (not directories)
        if len(name) > offset:
            # remove the common prefix
            zipinfo.filename = name[offset:]
            yield zipinfo


def in_memory_zip(files):
    """
    files is a list of tuples
    ('name in archive', 'data local vs bytes')
    this object can be directly uploaded to s3
    :param files:
    :return:
    """
    in_memory = BytesIO()
    zf = ZipFile(in_memory, mode="w")
    for file in files:
        with open(file, 'r') as myfile:
            zip_data = myfile.read()
        zf.writestr(file, zip_data)
    zf.close()
    in_memory.seek(0)
    data = in_memory.read()
    return data


def write_in_memory_zip_to_file(data: BytesIO, filename: str):
    """
    take a bytes io data and write to a file
    :param data:
    :param filename:
    :return:
    """
    with open(filename, 'wb') as w:
        w.write(data)
    return filename
