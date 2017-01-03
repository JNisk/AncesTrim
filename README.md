# AncesTrim tool

This tool is used to trim complex pedigree data and produce a minimum
pedigree while preserving critical relatedness information. It is
intended for genetics researchers and others who work with genealogical
information.

# Requirements

This script has been tested with Python 2.6.6 in a Linux environment,
and compatibility with other versions or operating systems is not
guaranteed. There are no modules that need to be installed.

# Installation

1. The script is ready for use. Simply unzip the package to a desired
location.

# Usage

The script requires two input files:
1. a tab-delimited text file containing pedigree data with one
individual per row (the raw rile)
2. a one-column text file containing individuals for whom the pedigree
will be constructed with one individual per row (the register file).

The script produces three output files:
1. a tab-delimited text file containing the minimum amount of
individuals needed to construct the pedigree
2. a GEDCOM 5.5 format file with the minimum individuals
3. a log file.

## How to run the script

The package includes example data that is located in the example_data
folder. To run the script, type the following on the command line:

```
python ancestrim.py --folder [folder name] --raw [raw file name]
--register [register file name] --out [output file name] --gen [N]
```

The folder name indicates the location of the input files and the
destination of the output files. As for now, the use of the folder
parameter is mandatory and there is no possibility to have the input
and output files in different folders. The raw and register file names
refer to the input files, e.g. `example1_raw.txt` and
`example1_register.txt.`

The output file name is the intended name for the files that will be
produced. Do not include any filename extensions in this, as they will
be added automatically. For example, `--out myfile` will create files
`myfile_pruned.txt`, `myfile_clean.ged` and `myfile.log`.

The generation parameter determines the maximum number of generations
that will be included while constructing and trimming the pedigree,
i.e. 3 generations means that a given individual's parents,
grandparents and great-grandparents will be included. Note that an
individual might nonetheless be discarded from the final output
pedigree if they don't match any of the script's relatedness evaluation
criteria.

## Pedigree trimming principles

This tool aims to simplify inherently complex pedigrees where the
the degree of inbreeding might be high. In such pedigrees, two
individuals can be related to each other via more than one common
ancestor, or an individual can be related to itself if an ancestor is
present in more than one lineage. In genetic studies, these kind of
relatedness structures can be very important, so the tool preserves
these relationships while discarding uninformative ones. Based on this
principle, the tool creates relatedness paths and evaluates them
according to the following criteria:

1. All queried individuals (i.e. the individuals in the register file)
are essential for the pedigree.
2. If two queried individuals are related to each other via a common
ancestor, then those paths are essential for the pedigree.
3. If a queried individual has an ancestor that is present in more than
one path, then those paths are essential for the pedigree.

To further elaborate on the concept of essential paths, not all
individuals on a given path are informative. For example, a common
ancestor of two individuals is important, but that ancestor's parents
may not necessarily be informative. Finally, one the minimum
individuals are collected, mates for all individuals are included
unless an individual is in the lowest position in all of its paths.

## Functions

Some functions are imported from ancestrim_module.py upon initiating
the script. The functions include:

* func_exit: Print an exit message and exit script.
* handle_unicode: A custom function for formatting special characters.
* open_rawfile: Open raw file and write its contents to a dict object.
* open_registerfile: Open register file and write to a list.
* parse_commandline: Parse parameters from command line with syntax
--option [filename] and return a dict object.
* write_gedcom: Take a filename, folder and list of pedigree data dicts
and write to GEDCOM file format (.ged).
* write_raw:  Take a filename, folder, a list of pedigree data dicts and
optionally list of config options and write data to raw file.
* write_log: Write information about the run to a log file.

For a more detailed description of the functions, use the standard
Python help function:

```
>>> import ancestrim_module
>>> help(ancestrim_module)
```

# Contact information

For contributions, bug reports or support contact
julia.niskanen@helsinki.fi.

# Changelog

1.0 Initial publication.
