import opendp.trans as trans 
from opendp_logger import Transformation, wrapper

for f in dir(trans):
    if f[:5] == "make_":
        locals()[f] = wrapper(f, getattr(trans, f), 'trans')

