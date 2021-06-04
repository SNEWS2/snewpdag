# Core module

This module contains the core code.

At this point that just means Node and the application module.

## Application

`app.py` contains the stand-alone application, which can be run
as a python module.  From the root directory of the package,
```
  python -m snewpdag [-h] [--input FILE] [--log LOG] config
```
The `config` argument is required to be a filename with
the configuration JSON.

The application takes input JSON from stdin by default,
but `--input` can be used to specify a file (or just pipe it
in through stdin).

The logging level is specified using `--log`.  Python logging level
strings are accepted, e.g.,
```
  python -m snewpdag --log=INFO snewpdag/data/test-flux-config.json
```

### Configuration CSV

The easiest way to configure a DAG is probably to use a CSV file,
which can be edited using a text editor or spreadsheet.

If the first column in a row is non-empty, it is taken to be a
node-configuring row.  The columns are as follows:
1. name:  the name of the node
1. class:  the name of the Node subclass
1. observe:  a comma-separated list of nodes to observe
1. kwargs:  keyword arguments for instantiating the node
Unquoted whitespace is ignored.  The kwargs argument looks like a
python dictionary, but without the external braces.

If the first column is empty, the row is taken to be a comment row.
You can also leave rows blank, so you can group nodes in your
spreadsheet and even label the groups with a title in the second
(or later) column.

### Configuration JSON

The configuration document is an array of dictionaries,
each dictionary specifying a node.
While the dictionary can be in JSON form,
it actually uses the more flexible python dictionary syntax.

For each node, the dictionary contains the following fields:

Field       | Description
------------|------------
`'name'`    | (required) name of the node
`'class'`   | (required) name of Node subclass
`'kwargs'`  | (optional) keyword arguments for instantiating node
`'observe'` | (optional) array of names to observe

In order for one node to observe another, the observed node must have been
defined earlier in the array.

(Note that the `observe` field doesn't really mean anything for input
nodes, but in principle there's no reason it can't be used, such as in
a DAG of inputs.)

### Input data JSON

The input can be provided as a JSON document using the
`--input` command-line argument with the filename.
If this optional argument is not provided, the
application will take input from stdin.

The input consists of an array of dictionaries.
Each dictionary forms a notification of one input node.
The fields for each object:

Field      | Description
-----------|------------
`'name'`   | the node into which the data will be injected via `notify()`
`'action'` | the type of update

Possible values of `action`:

Value      | Description
-----------|------------
`'alert'`  | update data associated with the named node
`'revoke'` | invalidate any previous data from the named node
`'reset'`  | invalidate all the data
`'report'` | report summary information

Other fields may be required by particular input nodes.

