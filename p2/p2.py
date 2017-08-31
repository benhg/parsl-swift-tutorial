from parsl import *

workers = ThreadPoolExecutor(max_workers=4)
dfk = DataFlowKernel(workers)


@App('bash', dfk)
def setup():
    """Set this example up as a bash app, which will call a command line argument"""
    cmd_line = "export PATH=$PWD/../app/:$PATH"


@App('bash', dfk)
def mysim(stdout="sim.out", stderr="sim.err"):
    """Run command line utility simulate with no params"""
    cmd_line = "simulate"


@App('python', dfk)
def many_sims(runs=10):
    """launch many concurrent simulations"""
    for i in range(runs):
        outputfile = "sim_{}".format(i)
        mysim(stdout="output/" + outputfile + ".out",
              stderr="output/" + outputfile + ".err")


if __name__ == '__main__':
    # use .result() function to force execution of next step to wait
    setup().result()
    many_sims()
