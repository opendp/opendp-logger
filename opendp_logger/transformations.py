import opendp.transformations as trans
from opendp_logger import wrapper

for f in dir(trans):
    if f.startswith("make_"):
        locals()[f] = wrapper(f, getattr(trans, f), "transformations")
