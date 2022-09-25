import opendp.meas as meas 
from opendp_logger import Measurement, wrapper

for f in dir(meas):
    if f[:5] == "make_":
        locals()[f] = wrapper(f, getattr(meas, f), 'meas')