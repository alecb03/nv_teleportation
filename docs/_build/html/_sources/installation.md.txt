# Installation

## Stable release

To install nv_teleportation, run this command in your terminal:

```sh
uv add nv_teleportation
```

Or if you prefer to use `pip`:

```sh
pip install nv_teleportation
```

## From source

The source files for nv_teleportation can be downloaded from the [Github repo](https://github.com/alecb03/nv_teleportation).

You can either clone the public repository:

```sh
git clone https://github.com/alecb03/nv_teleportation
```

Or download the [tarball](https://github.com/alecb03/nv_teleportation/tarball/main):

```sh
curl -OJL https://github.com/alecb03/nv_teleportation/tarball/main
```

Once you have a copy of the source, you can install it with:

```sh
cd nv_teleportation
uv sync
```
You will need an environment with the following packages:
* Python 3.11
* NumPy
* Simos
* Qutip
Once you have these packages installed, you can install nv_teleportation in the same
environment using
```sh
pip install -e .
```
from the top-level src/ nv_teleportation 
