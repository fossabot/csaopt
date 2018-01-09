# CSAOpt - A Cloud GPU based Simulated Annealing Optimization Framework.

[![Build Status](https://travis-ci.org/d53dave/csaopt.svg?branch=master)](https://travis-ci.org/d53dave/csaopt)
[![Coverage Status](https://coveralls.io/repos/github/d53dave/csaopt/badge.svg?branch=master)](https://coveralls.io/github/d53dave/csaopt?branch=master)

The main premise of this framework is that a user provides the implementation
for an abstract base class that describes the *standard* way of doing Simulated
Annealing while CSAOpt takes care of starting, configuring and running a
massively parallel flavor of Simulated Annealing on GPUs hosted in the cloud¹.

## Usage

TBD

### DISCLAIMER

If you are using CSAOpt together with AWS/EC2, this will incur costs on your
registered payment method (i.e. your credit card). CSAOpt will try to make sure
that instances are only run during normal operation, are properly shutdown when
the software terminates and will print a **big, fat warning** if it cannot
verify that everything was terminated upon exit.

I will not be responsible for any of the costs generated by using CSAOpt. This
software is provided **as is** and should be handled with the appropriate care.

**Always** [make sure that no instances are left running after CSAOpt terminates](https://console.aws.amazon.com/ec2/v2/).

## Configuration

The configuration is based on [HOCON](https://github.com/typesafehub/config/blob/master/HOCON.md)
(typesafe/lightbend) and integrated with the excellent [pyhocon](https://github.com/chimpler/pyhocon).
The main configuration (i.e. configuration for running the software) is located
in `conf/csaopt.conf`. In addition, there is an internal configuration file
under `app/internal/csaopt-internal.conf`, which does not need to be modified
under normal circumstances. A detailed description and listing of supported
configuration will follow here.

## Requirements

This software will not run on Windows out of the box, but it might run in the
[WSL](https://blogs.msdn.microsoft.com/wsl). It will probably run on MacOS, but
this is untested as of now. If you want to run it on a recent Linux
distribution, you are in luck. Development was done on 
[ElementaryOS](https://elementary.io/), while the deployed AWS instances are
based on Ubuntu Server 16.04 LTS.

Required software:

- A Conda3 distribution (i.e. [Anaconda](https://docs.anaconda.com/anaconda/install/)
or [Miniconda](https://conda.io/miniconda.html))
- [AWS](https://aws.amazon.com/) credentials or a local GPU capable of running
[CUDA](https://www.geforce.com/hardware/technology/cuda) computations.


## Development

Formerly based on [pipenv](https://github.com/pypa/pipenv) (which is awesome),
CSAOpt now uses Conda for package management.
Currently, there is no separate development environment, although this would
certainly be possible. So go ahead and

```bash
git clone https://github.com/d53dave/csaopt && cd csaopt
conda env create
source activate csaopt
```

for development.

Development of CSAOpt happened in VSCode, and it's required to set 

- `python.venvPath` to the venv path (see output of `conda env list`)
- `python.pythonPath` to `<your_venv_path>/bin/python`

for it to pick up the right interpreter and installed packages.

### Running the Test Suite

From inside the `virtualenv` (i.e. after executing `source active csaopt`), the
suite can be executed using

```bash
pytest
#or
py.test
```

### End-to-End Test

The end-to-end test suite is disabled by default, since it requires a complete
setup, i.e. including AWS credentials. Therefore, running the test will incur
some costs. The costs should be relatively low, given that the provided test
optimization should only run for a few seconds. AWS, however, charges a whole
hour even if the instances are terminated after a few seconds.

The AWS credentials for the end-to-end tests need to be provided as environment
variables, as documented in [awstools.py](app/aws/awstools.py).

The test suite is activated by setting a environment variable called
`CSAOPT_RUN_E2E`. The contents are irrelevant, it should evaluate to a
[truthy](https://docs.python.org/3/library/stdtypes.html#truth-value-testing)
value.

After setting the appropriate environment variables, the whole suite can be
executed and will include the end-to-end tests (see above). 

If you want to run
just the end-to-end tests, you can use the following command from the
`virtualenv`:

```bash
py.test -s test_e2e.py::test_end2end
```

## Cloud Computing Platforms

At this moment, only Amazon Web Services/EC2² is supported but it should be easy
to add support for other providers. In a nutshell, any provider that can be (1)
programmatically provisioned via public API, (2) provides CUDA capable hardware
and (3) can run the nvidia-docker tool *should* be able to support CSAOpt, since
deployment and most configuration is done via Docker. On AWS/EC2, CSAOpt uses an
AMI built by me, which has docker and nvidia-docker installed, as well as pulled
images. Without those, a complete installation would take several minutes for
each optimization run, and waiting makes people unhappy.

The script used to setup the CSAOpt AMI on AWS can be found in the
[setup-dockerhost.sh](app/docker/setup-dockerhost.sh) file. It can handle
Debian/Ubuntu and Fedora/CentOS based distributions.

Obvious candidates would be [Google Cloud Platform](https://cloud.google.com)
as well as [Microsoft Azure](https://azure.microsoft.com/en-us/), both of which
fulfill the 3 requirements stated above. Additionally, both providers
conveniently offer client libraries on PyPI. In case somebody wanted to add
support for another provider, the usual procedure would be:

1. Add client package from a repository (e.g. 
[google cloud from PyPI](https://pypi.python.org/pypi/google-cloud),
[azure-mgmt-compute from conda-forge](https://anaconda.org/conda-forge/azure-mgmt-compute))
2. Implement the [instancemanager interface](app/instancemanager/instancemanager.py),
see [awstools.py](app/aws/awstools.py)
3. Add `elif` branch to create the instance manager based on the config (TODO: where is this?)
4. Profit

## FAQs

> Why is this project not using docker to provision the message queue and workers?

It is! Things are a little bit awkward at the moment, since NVidia uses their
[own tool](https://github.com/NVIDIA/nvidia-docker) called Docker Engine Utility
for NVIDIA GPUs, which is not yet compatible with
[ECS](https://aws.amazon.com/ecs/) or other container services. This means that
we still rely on pre-built AMIs (or however images are called on other cloud 
providers), but when nvidia-docker becomes ready to be used with ECS, this will
rock. ~~That is a good question and it seems a very good use-case for docker,
especially since NVidia published an official
[Docker Engine Utility for NVIDIA GPUs](https://github.com/NVIDIA/nvidia-docker).
I am considering throwing out ansible (which is not meant to be used the way I
use it).~~

## Change History

> 0.2.0 Change to Numba for CUDA computations

With v0.2.0 the remaining `C++` code (i.e. directly interfacing with CUDA)
will be thrown out in favor of [Numba](https://github.com/numba/numba).
This will imply a switch from `pipenv` to `conda`, which is unfortunate, because
pipenv is really nice, IMHO. However, I don't want to compile llvmlite for the
deployments and I certainly don't want to have separate environment managers for
the different parts of this software.

The move to numba will also allow the project to move much closer to the initial
goal of using a single programming language for all components of CSAOpt, and
Python is a much nicer language than C++11, in my opinion.

> 0.1.0 Change to Python

With v0.1.0, most C++ code was abandoned. It became clear
that writing and maintaining this piece of software in C++
was never a good idea. Or, in other words, after chasing
obscure bugs where they should not be, I gave up. The initial
thought was **not to split the codebase into multiple languages** for
the sake of the current and future developers and maintainers.
This split will gradually be introduced, resulting, ideally, in
a structure where all glue code, i.e. config parsing, command line
interface, user interaction, networking and reporting will be
done in Python. The core concept of a user writing a small
model as C++ code which will be executed in a simulated annealing
pipeline on graphics processors will remain.

> 0.0.x C++ prototypes

Versions 0.0.x were prototypes written in C++,
including the proof of concept which was demo-ed to
my thesis supervisor and colleagues. These versions were
undocumented and development was sporadic. Most changes
did not make it into version control and features
were added and abandoned at will. The last version of the
C++ prototype in this repository was commit [6c922f](https://github.com/d53dave/csaopt/tree/6c922f933eceb8992e9acae36f1767336c56209f).

## Notes

¹ Only AWS EC2 and local GPUs are currently supported. Pull requests are welcome.

² There are plans to move to [ECS](https://aws.amazon.com/ecs/) once ECS
supports nvidia-docker **or** docker allows more capabilities in plugins so that
nvidia-docker can provide a proper docker plugin.
