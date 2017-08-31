from parsl import *

# Define our workers and dfk.
# In this case, we are running locally and specifying a max of 4
# concurrent threads
workers = ThreadPoolExecutor(max_workers=4)
dfk = DataFlowKernel(workers)

outputfile = "sim"


@App('bash', dfk)
def setup():
    """Set PATH to contain apps"""
    cmd_line = "export PATH=$PWD/../app:$PATH"


@App('bash', dfk)
def mysim(stdout="output/" + outputfile + ".out", stderr="output/" + outputfile + ".err"):
    """Set this example up as a bash app, which will call a command line utility, in this case simulate"""
    cmd_line = "simulate"


if __name__ == '__main__':
    setup().result()
    mysim()
