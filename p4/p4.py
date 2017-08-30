#!/usr/bin/env python3

from parsl import *
import parsl
#from parsl.execution_provider.midway.slurm import Midway

workers = IPyParallelExecutor(
    engine_json_file='~/.ipython/profile_default/security/ipcontroller-engine.json')

dfk = DataFlowKernel(workers)


def midway_setup():
    conf = {"site": "pool1",
            "queue": "bigmem",
            "maxnodes": 4,
            "walltime": '00:04:00',
            "controller": "10.50.181.1:50001"}

    pool1 = Midway(conf)
    pool1.scale_out(1)
    pool1.scale_out(1)


@App('bash', dfk)
def setup():
    cmd_line = "export PATH=$PWD/../app/:$PATH"

# Set this example up as a bash app, which will call a command line argument


@App('bash', dfk)
def sort(unsorted, stdout="output/sorted.out", stderr="output/sorted.err"):
    cmd_line = "sort {}".format(unsorted)


if __name__ == '__main__':
    setup()
    unsorted = "unsorted.txt"
    sorted = "output/sorted.txt"
    sort(unsorted, stdout=sorted)
