
from parsl import App, DataFlowKernel, ThreadPoolExecutor
from parsl.dataflow.futures import Future

workers = ThreadPoolExecutor(max_workers=4)
dfk = DataFlowKernel(workers)


@App('bash', dfk)
def setup()-> Future:
    """Set this example up as a bash app,
    which will call a command line argument"""
    cmd_line = "export PATH=$PWD/../app/:$PATH"


@App('bash', dfk)
def mysim(stdout: str="sim.out", stderr: str="sim.err")-> Future:
    """Run command line utility simulate with no params"""
    cmd_line = "simulate"


@App('python', dfk)
def many_sims(runs: int=10)-> Future:
    """launch many concurrent simulations"""
    for i in range(runs):
        outputfile = "sim_{}".format(i)
        mysim(stdout="output/" + outputfile + ".out",
              stderr="output/" + outputfile + ".err")


if __name__ == '__main__':
    # use .result() function to force execution of next step to wait
    setup().result()
    many_sims()
