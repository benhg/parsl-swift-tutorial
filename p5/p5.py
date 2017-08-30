#!/usr/bin/env python3

from parsl import *
import parsl
from parsl.execution_provider.midway.slurm import Midway

workers = IPyParallelExecutor(
    engine_json_file='~/.ipython/profile_default/security/ipcontroller-engine.json')


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
def mysim(stdout="sim.out", stderr="sim.err"):
    cmd_line = "simulate"


@App('python', dfk)
def start_many_sims(log_file, num_tasks=10):
    outputs = []
    deps = []
    for i in range(0, num_tasks):
        outputfile = "sim_{}".format(i)
        a = mysim(stdout=outputfile + ".out", stderr=log_file)
        outputs.append(outputfile + ".out")
        deps.append(a)
    return outputs, deps


@App('bash', dfk)
def stats(deps=[], inputs=[], stderr='average.err', stdout='average.out'):
    cmd_line = "stats {}".format(" ".join(inputs))


if __name__ == '__main__':
    setup()
    results = start_many_sims('sims.log', 100)
    inputs = results.result()[0]
    deps = [dep.result() for dep in results.result()[1]]
    stats(deps=deps, inputs=inputs)
