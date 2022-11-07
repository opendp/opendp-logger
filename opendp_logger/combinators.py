import opendp.combinators as comb
from opendp_logger import wrapper

for f in dir(comb):
    if f.startswith("make_"):
        locals()[f] = wrapper(f, getattr(comb, f), "combinators")
