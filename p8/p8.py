#!/usr/bin/env python3

from parsl import *
import parsl
import sys
import os

from parsl.execution_provider.midway.slurm import Midway

workers = IPyParallelExecutor()
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


@App('bash', dfk)
def compile_app():
    cmd_line = "mpicc ../mpi/pi.c -o mpi_pi"


@App('bash', dfk)
def mpi_pi(nproc, app, intervals, duration, mpilib='mpiexec', stdout="mpi_pi.out", stderr="mpi_pi.err"):
    cmd_line = "{} -np {} {} {} {}".format(mpilib,
                                           nproc, app, intervals, duration)


@App('python', dfk)
def many_mpi_pi(time, nproc, app, intervals, duration, n_runs=10):
    fus = []
    files = []
    for i in range(n_runs):
        outfile = "output/mpi_pi_{}.out".format(i)
        fus.append(mpi_pi(nproc, app, intervals, duration, stdout=outfile,
                          stderr="output/mpi_pi_{}.err".format(i)))
        files.append(outfile)
    return fus, files


@App('bash', dfk)
def summarize(pi_runs=[], deps=[], stdout="summarize.out", stderr="summarize.err"):
    cmd_line = 'grep "^pi" {}'.format(" ".join([str(i) for i in pi_runs]))


if __name__ == '__main__':
    setup()
    # use .result() to make the execution wait until the app has compiled
    compile_app().result()

    app = "{}/mpi_pi".format(os.getcwd())
    deps, files = many_mpi_pi(48, 10, app, 10, 10).result()
    print(files)
    summarize(pi_runs=files, deps=[dep.result() for dep in deps],
              stdout='output/summarize.out', stderr='output/summarize.err')
