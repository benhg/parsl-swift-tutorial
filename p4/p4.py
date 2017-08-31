#!/usr/bin/env python3

from parsl import App, DataFlowKernel, IPyParallelExecutor
from parsl.execution_provider.midway.slurm import Midway
from parsl.dataflow.futures import Future

"""From now on, the tutorial applications are written to run on Midway,
a cluster located at the University of Chicago Research Computing Center
They have also been tested locally on both Mac and Ubuntu Linux.
In order to run them locally, either start an
IPyParallel cluster controller on your machine
or change the workers to something like this:

workers = ThreadPoolExecutor(max_workers=NUMBER OF CORES)"""

# This is the default file location.
# I've left it in on the first example for clarity.
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
    """Set Path"""
    cmd_line = "export PATH=$PWD/../app/:$PATH"

# Set this example up as a bash app, which will call a command line argument


@App('bash', dfk)
def sort(unsorted: str, stdout: str="output/sorted.out",
         stderr: str="output/sorted.err")-> Future:
    """Call sort executable on file `unsorted`"""
    cmd_line = "sort {}".format(unsorted)


if __name__ == '__main__':
    setup()
    unsorted = "unsorted.txt"
    sorted = "output/sorted.txt"
    sort(unsorted, stdout=sorted)
