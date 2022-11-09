import pkg_resources

PT_TYPE_PREFIX = "py_type:"

try:
    OPENDP_VERSION = pkg_resources.get_distribution("opendp").version
except pkg_resources.DistributionNotFound:
    OPENDP_VERSION = "0.0.0+development"
