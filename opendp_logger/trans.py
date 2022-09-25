import opendp.trans as trans 
from opendp_logger import Transformation, wrapper

for f in dir(trans):
    locals()[f] = wrapper(f, getattr(trans, f))

