#!/usr/bin/env python3

from parsl import App, IPyParallelExecutor, DataFlowKernel
from parsl.execution_provider.midway.slurm import Midway
from parsl.dataflow.futures import Future

"""From now on, the tutorial applications are written to run on Midway,
a cluster located at the
University of Chicago Research Computing Center
They have also been tested locally on both Mac and Ubuntu Linux.
In order to run them locally, either
start an IPyParallel cluster controller on your machine
or change the workers to something like this:

workers = ThreadPoolExecutor(max_workers=NUMBER OF CORES)

This example is the same as p3.py, except run on Midway

"""

workers = IPyParallelExecutor(
    engine_json_file='~/.ipython/profile_default/security/ipcontroller-engine.json')
dfk = DataFlowKernel(workers)


@App('python', dfk)
def midway_setup()-> Future:
    """Set site-specific options"""
    conf = {"site": "pool1",
            "queue": "bigmem",
            "maxnodes": 4,
            "walltime": '00:04:00',
            "controller": "10.50.181.1:50001"}

    pool1 = Midway(conf)
    pool1.scale_out(1)
    pool1.scale_out(1)


@App('bash', dfk)
def setup()-> Future:
    """Set path"""
    cmd_line = "export PATH=$PWD/../app/:$PATH"


@App('bash', dfk)
def mysim(stdout: str="sim.out", stderr: str="sim.err")-> Future
    """Call simulate from the cli"""
    cmd_line = "simulate"


@App('python', dfk)
def start_many_sims(log_file: str, num_tasks: int=10)-> Future:
    """Start many concurrent simulations from parsl itself"""
    outputs = []
    deps = []
    for i in range(0, num_tasks):
        outputfile = "output/sim_{}".format(i)
        a = mysim(stdout=outputfile + ".out", stderr=log_file)
        outputs.append(outputfile + ".out")
        deps.append(a)
    return outputs, deps


@App('bash', dfk)
def stats(deps: list=[], inputs: list=[], stderr: str='output/average.err',
          stdout: str='output/average.out')-> Future:
    """Call stats with filnames passed in through `inputs`"""
    cmd_line = "stats {}".format(" ".join(inputs))


if __name__ == '__main__':
    setup()
    results = start_many_sims('output/sims.log', 100)
    # get all filenames
    inputs = results.result()[0]
    """
    get futures that stats depends on.
    Because we call with bash apps, we need
    to get the dependent futures separately
    if we were to rewrite with all python apps
    returning filenames, we could simply pass
    the futures themselves into the next layer
    of apps and execution would wait automatically"""

    deps = [dep.result() for dep in results.result()[1]]
    stats(deps=deps, inputs=inputs)
