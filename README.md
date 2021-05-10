# snewpdag

SNEWS2 alert (pointing) calculations.

Please see the wiki for information on setting up and developing
code, and for module documentation.

## Installation

Ther `requirements.txt` file now includes `numpy` and `healpy` in
anticipation of needing these.  They can be installed using `pip`,
though in the case of `healpy` I needed to install one of its
dependencies explicitly.  (Details:  this was the `cfitsio` library,
which supposedly is included in `healpy`.  The build process didn't
seem to find the resulting local cfitsio library, so instead I
installed the `libcfitsio-dev` package on my Ubuntu 16 system.)

## Usage

The `Makefile` contains recipes for initialization, running the
application, and running unit tests.

Note that so far we've been developing with unit tests.
The application itself hasn't been tested yet; it will use input
files (in the `data` directory) and generate some kind of output.

### External packages

`lightcurve_match` has been linked as a submodule.
To clone `lightcurve_match` along with `snewpdag`,
```
  git clone --recurse-submodules
```
If you've already cloned, you'll see an empty `externals/lightcurve_match`
subdirectory under `snewpdag`.  The following commands will populate it:
```
  git submodule init
  git submodule update
```
This package requires ROOT, so set it up now, and then
```
  make lightcurvesim
```

## Development

1. Make a new branch in which you develop your plugin.
1. Add algorithm code to the `plugins` directory.
1. You will probably also want to list your plugin in
   `plugins/__init__.py` so it can be imported easily.
1. Write unit tests at thes ame time.  See the `tests` directory for examples.
1. Add the command line for running your tests to the `test` target
   in the `Makefile`.
1. When your plugin is ready, push your branch to the SNEWS repository
   and make a pull request.

