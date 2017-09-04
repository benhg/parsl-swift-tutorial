from parsl import App, DataFlowKernel, ThreadPoolExecutor
from parsl.dataflow.futures import Future

workers = ThreadPoolExecutor(max_workers=4)
dfk = DataFlowKernel(workers)


@App('bash', dfk)
def setup()-> Future:
    """set PATH"""
    cmd_line = "export PATH=$PWD/../app/:$PATH"


@App('bash', dfk)
def mysim(stdout: str="sim.out", stderr: str="sim.err", outputs: list=[])-> Future:
    """Call simulate on the command line"""
    cmd_line = "simulate"


@App('python', dfk)
def start_many_sims(num_tasks: int=10)-> Future:
    """Start many concurrent simulations on the command line"""
    outputs = []
    for i in range(0, num_tasks):
        outputfile = "output/sim_{}".format(i)
        a = mysim(stdout=outputfile + ".out", stderr=outputfile +
                  ".err", outputs=[outputfile + ".out"])
        outputs.append(a)
    return outputs


@App('bash', dfk)
def stats(inputs: list=[],
          stderr: str='output/average.err',
          stdout: str='output/average.out')-> Future:
    """call stats cli utility with all simulations ans inputs"""
    cmd_line = "stats {}".format(" ".join(inputs))


if __name__ == '__main__':
    # Make execution wait until after path is set
    setup().result()
    results = [i[1][0].result() for i in start_many_sims().result()]
    print(results)
    # Get filenames of simulation outputs
    # Get futures that the stats function will depend on.
    # pass dependencies into stats function
    stats(inputs=results)
