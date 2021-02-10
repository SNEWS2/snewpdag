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

### Configuration JSON

The configuration document is an array of dictionaries,
each dictionary specifying a node.

There are three general varieties of node, all of which subclass Node:

Type   | Description
-------|------------
input  | validates input data, can be observed by other nodes for updates
output | turns data into an outside-facing alert
normal | performs some kind of computation

However, we don't enforce strict boundaries for now.

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

Other fields may be required by particular input nodes.

In order to clear the DAG of input state, issue a `revoke` for
all inputs.  (In fact, this may be a reason to define a master revocation
node which all input nodes observe for just this message.
Data is still injected in the same way.)

