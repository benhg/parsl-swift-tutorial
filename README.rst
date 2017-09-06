Parsl is a simple scripting library for executing dataflow-based dependency in Python.

Parsl allows you to define a dependency based graph of what various applications need in order to be executed.

While you can write arbitrary programs directly in Pars, one of the things Parsl is good at is acting like a structured "shell" language. 
It runs programs concurrently as soon as their inputs are available, reducing the need for complex parallel programming. Parsl expresses workflow in a portable fashion: The same script can run on multicore computers, clusters, clouds, grids, and supercomputers.

In every example, you will find a parsl script that executes the workflow pattern as well as the equivalent swift code that the parsl was created from. In most cases, there is also a visual representation of the workflow.

In this tutorial, you will be able to first try a few Parsl examples (examples 1-3) on your local machine, to get a sense of the language. Then, in examples 4-6 you will run similar workflows on any resource you may have access to, such as clouds (Amazon Web Services), Cray HPC systems, clusters etc, and see how more complex workflows can be expressed with Parsl scripts.

Examples 4-6 can also be run on a local multicore machine if desired.

To run the tutorial, ensure that Python (3.5+) and parsl 0.2 is installed on the machine you would be using to run the tutorial on.

To install Parsl:
  1. Download Parsl::

    $ git clone https://github.com/Parsl/parsl.git parsl

  2. Install::

    $ cd parsl
    
    $ python3 setup.py install

Setup the Parsl tutorial::

    $ git clone https://github.com/benhg/parsl-swift-tutorial.git parsl_tutorial
 
    $ cd parsl_tutorial
  
    $ bash setup.sh
    
Doing this will add the sample applications ``simulate`` and ``stats`` (mock "science" applications) and some other functionalities to your local $PATH for you to run the tutorial.

See the link https://nbviewer.jupyter.org/github/benhg/parsl-swift-tutorial/blob/master/entire-parsl-tutorial.ipynb for a static view of the enire tutorial in a Jupyter Notebook.
