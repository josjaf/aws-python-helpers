def dict_to_tags(tags_dict):
    tags = [{"Key": k, "Value": v} for k, v in tags_dict.items()]
    return tags

def aws_tags_to_dict(resource, dict_key_key="Key", dict_key_value="Value"):
    """
    convert a list of dicts to a flattened dict
    :param resource:
    :param dict_key_key:
    :param dict_key_value:
    :return:
    """
    return dict((tag[dict_key_key], tag[dict_key_value]) for tag in resource)
