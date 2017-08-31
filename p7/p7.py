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
    cmd_line = "mpicc ../mpi/mpi_hello.c -o mpi_hello"


@App('bash', dfk)
def mpi_hello(time, nproc, app, mpilib='mpiexec', stdout="mpi_hello.out", stderr="mpi_hello.err"):
    cmd_line = "{} -np {} {} {}".format(mpilib, nproc, app, time)


@App('python', dfk)
def many_mpi_hello(time, nproc, app, n_runs):
    fus = []
    for i in range(n_runs):
        print(i)
        fus.append(mpi_hello(time, nproc, app, stdout="output/mpi_hello_{}.out".format(i),
                             stderr="output/mpi_hello_{}.err".format(i)))
    return fus


if __name__ == '__main__':
    setup()
    # use .result() to make the execution wait until the app has compiled
    compile_app().result()

    app = "{}/mpi_hello".format(os.getcwd())
    print(many_mpi_hello(1400000, 10, app, 10).result())
