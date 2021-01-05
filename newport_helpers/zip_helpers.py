# get a common prefix
import os
from io import BytesIO
from zipfile import ZipFile
class ZipHelpers():
    def __init__(self, *args, **kwargs):
        return

    def get_members(self, zip):
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
    def in_memory_zip(self, files):
        """
        files is a list of tuples
        ('name in archive', 'data local vs bytes')
        :param files:
        :return:
        """
        in_memory = BytesIO()
        zf = ZipFile(in_memory, mode="w")
        for file in files:
            zf.writestr(file[0], data)
        zf.close()
        in_memory.seek(0)
        data = in_memory.read()
        return data