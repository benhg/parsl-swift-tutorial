from parsl import App, DataFlowKernel, ThreadPoolExecutor
from parsl.dataflow.futures import Future

workers = ThreadPoolExecutor(max_workers=4)
dfk = DataFlowKernel(workers)


@App('bash', dfk)
def setup()-> Future:
    """set PATH"""
    cmd_line = "export PATH=$PWD/../app/:$PATH"


@App('bash', dfk)
def mysim(stdout: str="sim.out", stder: str="sim.err")-> Future:
    """Call simulate on the command line"""
    cmd_line = "simulate"


@App('python', dfk)
def start_many_sims(num_tasks: int=10)-> Future:
    """Start many concurrent simulations on the command line"""
    outputs = []
    deps = []
    for i in range(0, num_tasks):
        outputfile = "output/sim_{}".format(i)
        a = mysim(stdout=outputfile + ".out", stderr=outputfile + ".err")
        outputs.append(outputfile + ".out")
        deps.append(a)
    return outputs, deps


@App('bash', dfk)
def stats(deps: list=[], inputs: list=[],
          stderr: str='output/average.err',
          stdout: str='output/average.out')-> Future:
    """call stats cli utility with all simulations ans inputs"""
    cmd_line = "stats {}".format(" ".join(inputs))


if __name__ == '__main__':
    # Make execution wait until after path is set
    setup().result()

    results = start_many_sims()
    # Get filenames of simulation outputs
    inputs = results.result()[0]
    # Get futures that the stats function will depend on.
    # making the entire workflow wait until the next step is ready
    deps = [dep.result() for dep in results.result()[1]]
    # pass dependencies into stats function
    stats(deps=deps, inputs=inputs)
