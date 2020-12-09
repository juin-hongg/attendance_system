import yaml
import os
from my_logging import my_logging

logger = my_logging.get_logger(__name__)


def read_yaml_file(filename):
    """
    Read credentials through environment variables
    """
    logger.info("Reading YAML file...")

    with open(filename, 'r') as file:
        cfg = yaml.safe_load(file)

    return cfg


class EnvTag(yaml.YAMLObject):
    """
    Class to convert from yaml object or to yaml object
    """
    yaml_tag = u'!ENV'

    def __init__(self, env_var):
        self.env_var = env_var

    def __repr__(self):
        return os.environ.get(self.env_var)

    @classmethod
    def from_yaml(cls, loader, node):
        return EnvTag(node.value)

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_scalar(cls.yaml_tag, data.env_var)

yaml.SafeLoader.add_constructor("!ENV", EnvTag.from_yaml)
yaml.SafeDumper.add_multi_representer(EnvTag, EnvTag.to_yaml)
