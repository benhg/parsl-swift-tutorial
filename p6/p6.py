#!/usr/bin/env python3

from parsl import *
import parsl

from parsl.execution_provider.midway.slurm import Midway

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
def simulation(timesteps, sim_range, bias_file, scale, sim_count, seed_file, stdout='sim.out',  stderr='sim.err'):
    cmd_line = 'simulate -t {} -r {} -B {} -x {} -n {} -S {}'.format(
        timesteps, sim_range, bias_file, scale, sim_count, seed_file)
    print()


@App('python', dfk)
def start_many_sims(steps, sim_range, sim_count, log_file, num_tasks=10):
    outputs = []
    deps = []
    for i in range(0, num_tasks):
        outputfile = "sim_{}".format(i)
        biasfile = "bias_{}.out".format(i)
        a = simulation(steps, sim_range, biasfile, 1000000, sim_count,
                       'seed.out', stdout=outputfile + ".out", stderr=log_file)
        outputs.append(outputfile + ".out")
        deps.append(a)
    return outputs, deps


@App('bash', dfk)
def stats(deps=[], inputs=[], stderr='average.err', stdout='average.out'):
    cmd_line = "stats {}".format(" ".join(inputs))


@App('bash', dfk)
def gen_seed(n_seeds, r, generate_script, stdout='seed.out', stderr='seed.err'):
    cmd_line = "{} -r {} -n {}".format(generate_script, r, n_seeds)


@App('bash', dfk)
def calc_bias(bias_range, n_values, bias_script, stdout='bias.out', stderr='bias.err'):
    cmd_line = "{} -r {} -n {}".format(bias_script, bias_range, n_values)


@App('python', dfk)
def start_many_bias(bias_range, n_values, bias_script, log_file, num_tasks=10):
    outputs = []
    deps = []
    for i in range(0, num_tasks):
        outputfile = "bias_{}".format(i)
        a = calc_bias(bias_range, n_values, bias_script,
                      stdout=outputfile + ".out", stderr=log_file)
        outputs.append(outputfile + ".out")
        deps.append(a)
    return outputs, deps


if __name__ == '__main__':
    setup()
    deps = []

    seedfile = 'seed.out'
    seed = gen_seed(1, 200000, "simulate")
    deps.append(seed)

    biases = start_many_bias(1000, 20, 'simulate', "bias.err")
    deps.extend(biases.result()[1])

    steps = 1
    sim_range = 100
    n_sim = 10
    all_sims = start_many_sims(steps, sim_range, n_sim, "sims.err")
    deps.extend([all_sims.result()[1][i].result()
                 for i in range(len(all_sims.result()[1]))])

    averages = all_sims.result()[0]
    stats(deps=deps, inputs=averages)
