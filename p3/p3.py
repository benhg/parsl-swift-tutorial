from parsl import *

workers = ThreadPoolExecutor(max_workers=4)
dfk = DataFlowKernel(workers)


@App('bash', dfk)
def setup():
    cmd_line = "export PATH=$PWD/../app/:$PATH"

# Set this example up as a bash app, which will call a command line argument


@App('bash', dfk)
def mysim(stdout="sim.out", stderr="sim.err"):
    cmd_line = "simulate"


@App('python', dfk)
def start_many_sims(num_tasks=10):
    outputs = []
    deps = []
    for i in range(0, num_tasks):
        outputfile = "output/sim_{}".format(i)
        a = mysim(stdout=outputfile + ".out", stderr=outputfile + ".err")
        outputs.append(outputfile + ".out")
        deps.append(a)
    return outputs, deps


@App('bash', dfk)
def stats(deps=[], inputs=[], stderr='output/average.err', stdout='output/average.out'):
    cmd_line = "stats {}".format(" ".join(inputs))


if __name__ == '__main__':
    setup()
    results = start_many_sims()
    inputs = results.result()[0]
    deps = [dep.result() for dep in results.result()[1]]
    stats(deps=deps, inputs=inputs)
