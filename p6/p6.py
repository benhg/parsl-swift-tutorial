#!/usr/bin/env python3

from parsl import *
import parsl

from parsl.execution_provider.midway.slurm import Midway

workers = IPyParallelExecutor(
    engine_json_file='~/.ipython/profile_default/security/ipcontroller-engine.json')
dfk = DataFlowKernel(workers)

"""From now on, the tutorial applications are written to run on Midway, 
a cluster located at the University of Chicago Research Computing Center. 
They have also been tested locally on both Mac and Ubuntu Linux. 
In order to run them locally, either start an IPyParallel cluster controller on your machine 
or change the workers to something like this:

workers = ThreadPoolExecutor(max_workers=NUMBER OF CORES)

This example is the same as p5.py, except with more layers of dependence added.

"""


def midway_setup():
    """Set site-specific options for midway"""
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
    """set PATH"""
    cmd_line = "export PATH=$PWD/../app/:$PATH"

# Set this example up as a bash app, which will call a command line argument


@App('bash', dfk)
def simulation(timesteps, sim_range, bias_file, scale, sim_count, seed_file, stdout='sim.out',  stderr='sim.err'):
    """Call simulation from cli with input values from seed and bias files"""
    cmd_line = 'simulate -t {} -r {} -B {} -x {} -n {} -S {}'.format(
        timesteps, sim_range, bias_file, scale, sim_count, seed_file)
    print()


@App('python', dfk)
def start_many_sims(steps, sim_range, sim_count, log_file, num_tasks=10):
    """Launch many concurrent simulations with input values from seed and bias files"""
    outputs = []
    deps = []
    for i in range(0, num_tasks):
        outputfile = "output/sim_{}".format(i)
        biasfile = "output/bias_{}.out".format(i)
        a = simulation(steps, sim_range, biasfile, 1000000, sim_count,
                       'output/seed.out', stdout=outputfile + ".out", stderr=log_file)
        outputs.append(outputfile + ".out")
        deps.append(a)
    return outputs, deps


@App('bash', dfk)
def stats(deps=[], inputs=[], stderr='output/average.err', stdout='output/average.out'):
    """Launch stats calculation with all input files passed through `inputs`"""
    cmd_line = "stats {}".format(" ".join(inputs))


@App('bash', dfk)
def gen_seed(n_seeds, r, generate_script, stdout='output/seed.out', stderr='output/seed.err'):
    """Generate seed file from simulate executable"""
    cmd_line = "{} -r {} -n {}".format(generate_script, r, n_seeds)


@App('bash', dfk)
def calc_bias(bias_range, n_values, bias_script, stdout='bias.out', stderr='bias.err'):
    """Generate bias file from simulate executable"""
    cmd_line = "{} -r {} -n {}".format(bias_script, bias_range, n_values)


@App('python', dfk)
def start_many_bias(bias_range, n_values, bias_script, log_file, num_tasks=10):
    """Launch many concurrent bias simulations with input values from seed files"""
    outputs = []
    deps = []
    for i in range(0, num_tasks):
        outputfile = "output/bias_{}".format(i)
        a = calc_bias(bias_range, n_values, bias_script,
                      stdout=outputfile + ".out", stderr=log_file)
        outputs.append(outputfile + ".out")
        deps.append(a)
    return outputs, deps


if __name__ == '__main__':
    setup()
    deps = []

    # Generate seed file
    seedfile = 'seed.out'
    seed = gen_seed(1, 200000, "simulate")
    deps.append(seed)

    # Generate a bias file for each simulation
    biases = start_many_bias(1000, 20, 'simulate', "output/bias.err")
    deps.extend(biases.result()[1])

    steps = 1
    sim_range = 100
    n_sim = 10
    # run simulations only after seed and bias files are ready
    all_sims = start_many_sims(steps, sim_range, n_sim, "output/sims.err")
    deps.extend([all_sims.result()[1][i].result()
                 for i in range(len(all_sims.result()[1]))])

    # run stats only after all sims are complete
    averages = all_sims.result()[0]
    stats(deps=deps, inputs=averages)
