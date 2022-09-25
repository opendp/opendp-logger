import opendp.comb as comb 
from opendp_logger import wrapper

for f in dir(comb):
    locals()[f] = wrapper(f, getattr(comb, f), 'comb')