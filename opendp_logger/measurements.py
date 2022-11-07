import opendp.measurements as meas
from opendp_logger import wrapper

for f in dir(meas):
    if f.startswith("make_"):
        locals()[f] = wrapper(f, getattr(meas, f), "measurements")
