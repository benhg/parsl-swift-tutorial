from parsl import *

workers = ThreadPoolExecutor(max_workers=4)
dfk = DataFlowKernel(workers)

outputfile = "sim"


@App('bash', dfk)
def setup():
    cmd_line = "export PATH=$PWD/../app:$PATH"

# Set this example up as a bash app, which will call a command line argument


@App('bash', dfk)
def mysim(stdout="output/" + outputfile + ".out", stderr=outputfile + ".err"):
    cmd_line = "simulate"


if __name__ == '__main__':
    setup()
    mysim()
