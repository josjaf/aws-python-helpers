import hashlib
import newport_helpers
logger = newport_helpers.nph.logger

def string_md5_compare(string1, string2):
    # TODO why would you use this instead of ==? Maybe ssh keys or something like that
    """
    compare the md5 of two strings
    :param string1:
    :param string2:
    :return:
    """
    test1 = hashlib.md5(string1.encode('utf-8')).hexdigest()
    test2 = hashlib.md5(string2.encode('utf-8')).hexdigest()
    assert test1 == test2
    # if this statement not, get assert error
    logger.info("MD5 Match")
    return


def file_to_string(file):
    with open(file, 'r') as myfile:
        file_str = myfile.read()
    myfile.close()

    return file_str


def compare_md5_file(file1_path, file2_path):
    """
    compare the md5 of two files
    :param file1_path:
    :param file2_path:
    :return:
    """
    md5_1 = (file_to_string(file1_path)).encode()

    md5_2 = (file_to_string(file2_path)).encode()
    file1_md5 = hashlib.md5(md5_1).hexdigest()
    file2_md5 = hashlib.md5(md5_2).hexdigest()

    if file1_md5 != file2_md5:
        raise Exception("Original File and Parameter Store File do not have the same MD5")
    else:
        logger.info("SUCCESS MD5 Match")

    assert file1_md5 == file2_md5
    return
