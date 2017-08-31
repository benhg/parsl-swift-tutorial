#!/usr/bin/env python3

from parsl import *
import parsl
import sys
import os

from parsl.execution_provider.midway.slurm import Midway

"""From now on, the tutorial applications are written to run on Midway, 
a cluster located at the University of Chicago Research Computing Center. 
They have also been tested locally on both Mac and Ubuntu Linux. 
In order to run them locally, either start an IPyParallel cluster controller on your machine 
or change the workers to something like this:

workers = ThreadPoolExecutor(max_workers=NUMBER OF CORES)

This example is the same as p3.py, except run on Midway

""""""From now on, the tutorial applications are written to run on Midway, 
a cluster located at the University of Chicago Research Computing Center. 
They have also been tested locally on both Mac and Ubuntu Linux. 
In order to run them locally, either start an IPyParallel cluster controller on your machine 
or change the workers to something like this:

workers = ThreadPoolExecutor(max_workers=NUMBER OF CORES)
"""

workers = IPyParallelExecutor()
dfk = DataFlowKernel(workers)


def midway_setup():
    """Set Midway site-specific options"""
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
    """Set path"""
    cmd_line = "export PATH=$PWD/../app/:$PATH"


@App('bash', dfk)
def compile_app(compiler="mpicc"):
    """Compile mpi app with mpicc"""
    cmd_line = "{} ../mpi/mpi_hello.c -o mpi_hello".format(compiler)


@App('bash', dfk)
def mpi_hello(time, nproc, app="mpi_hello", mpilib="mpiexec", stdout="mpi_hello.out", stderr="mpi_hello.err"):
    """Call compiled mpi executable with mpilib. 
    Works natively for openmpi mpiexec, mpirun, orterun, oshrun, shmerun
    mpiexec is default"""
    cmd_line = "{} -np {} {} {}".format(mpilib, nproc, app, time)


@App('python', dfk)
def many_mpi_hello(time, nproc, app, n_runs):
    """Call mpi hello world n_runs times"""
    fus = []
    for i in range(n_runs):
        fus.append(mpi_hello(time, nproc, app, stdout="output/mpi_hello_{}.out".format(i),
                             stderr="output/mpi_hello_{}.err".format(i)))
    return fus


if __name__ == '__main__':
    setup()
    # use .result() to make the execution wait until the app has compiled
    compile_app().result()

    app = "{}/mpi_hello".format(os.getcwd())
    many_mpi_hello(1400000, 10, app, 10)
