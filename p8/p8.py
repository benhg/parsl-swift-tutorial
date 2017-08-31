#!/usr/bin/env python3
import os

from parsl import App, DataFlowKernel, IPyParallelExecutor
from parsl.dataflow.futures import Future
from parsl.execution_provider.midway.slurm import Midway

"""From now on, the tutorial applications are written to run on Midway,
a cluster located at the University of Chicago Research Computing Center
They have also been tested locally on both Mac and Ubuntu Linux.
In order to run them locally,
either start an IPyParallel cluster controller on your machine
or change the workers to something like this:

workers = ThreadPoolExecutor(max_workers=NUMBER OF CORES)
"""

workers = IPyParallelExecutor()
dfk = DataFlowKernel(workers)


@App('python', dfk)
def midway_setup()-> Future:
    """Set midway specific site options"""
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
    """Set PATH"""
    cmd_line = "export PATH=$PWD/../app/:$PATH"


@App('bash', dfk)
def compile_app()->Future:
    """Compile MPI app with mpi compiler"""
    cmd_line = "mpicc ../mpi/pi.c -o mpi_pi"


@App('bash', dfk)
def mpi_pi(nproc: int, intervals: int, duration: int, app: str="mpi_pi",
           mpilib: str='mpiexec', stdout: str="mpi_pi.out",
           stderr: str="mpi_pi.err")-> Future:
    """Call mpi_pi from cli"""
    cmd_line = "{} -np {} {} {} {}".format(mpilib,
                                           nproc, app, intervals, duration)


@App('python', dfk)
def many_mpi_pi(time: int, nproc: int, app: int, intervals: int,
                duration: int, n_runs: int=10)-> Future:
    """Call many copies of mpi_pi concurrently"""
    fus = []
    files = []
    for i in range(n_runs):
        outfile = "output/mpi_pi_{}.out".format(i)
        fus.append(mpi_pi(nproc, app, intervals, duration, stdout=outfile,
                          stderr="output/mpi_pi_{}.err".format(i)))
        files.append(outfile)
    return fus, files


@App('bash', dfk)
def summarize(pi_runs: list=[], deps: list=[], stdout: str="summarize.out",
              stderr: str="summarize.err")-> Future:
    """Create summary file"""
    cmd_line = 'grep "^pi" {}'.format(" ".join([str(i) for i in pi_runs]))


if __name__ == '__main__':
    setup()
    # use .result() to make the execution wait until the app has compiled
    compile_app().result()

    """
    get futures that stats depends on.
    Because we call with bash apps, we need to get the dependent futures separately
    if we were to rewrite with all python apps returning filenames, we could simply pass
    the futures themselves into the next layer of apps and execution would wait automatically
    """

    app = "{}/mpi_pi".format(os.getcwd())
    deps, files = many_mpi_pi(48, 10, app, 10, 10).result()
    print(files)
    summarize(pi_runs=files, deps=[dep.result() for dep in deps],
              stdout='output/summarize.out', stderr='output/summarize.err')
