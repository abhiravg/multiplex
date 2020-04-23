# Multiplex: Simple, elegant and composable configurations.

This library relies on [argparse](https://docs.python.org/3.8/library/argparse.html) 
and [configurator](https://configurator.readthedocs.io/en/latest/index.html) in order to 
bring you command line interfaces (CLIs) that are dynamically created, with arguments that are 
automatically parsed and merged with any default configurations the program may have. The result 
is a well-structured config object that can be used in a wide range of applications.

## Simple Use Cases

<details>
<summary>Generate CLI from config</summary>
<p>

If you already use a configuration object (dict, string, a yaml file or otherwise), 
you can generate a simple CLI from it. Here's a simple example using flask:

```python
from flask import Flask
from multiplex import Multiplexor

app = Flask(__name__)

m = Multiplexor(dict(app.config))
args = m.get_conf()
app.config.update(args.data)
```

This takes flask's default config, exposes a corresponding CLI that 
let's you override any parameters and then updates these defaults. 
Here's the generated CLI:

```
multiplex\examples> python3 server.py -h
usage: server.py [-h] [--ENV] [--DEBUG] [--TESTING] [--PROPAGATE_EXCEPTIONS]
                 [--PRESERVE_CONTEXT_ON_EXCEPTION] [--SECRET_KEY]
                 [--PERMANENT_SESSION_LIFETIME] [--USE_X_SENDFILE]
                 [--SERVER_NAME] [--APPLICATION_ROOT] [--SESSION_COOKIE_NAME]
                 [--SESSION_COOKIE_DOMAIN] [--SESSION_COOKIE_PATH]
                 [--SESSION_COOKIE_HTTPONLY] [--SESSION_COOKIE_SECURE]
                 [--SESSION_COOKIE_SAMESITE] [--SESSION_REFRESH_EACH_REQUEST]
                 [--MAX_CONTENT_LENGTH] [--SEND_FILE_MAX_AGE_DEFAULT]
                 [--TRAP_BAD_REQUEST_ERRORS] [--TRAP_HTTP_EXCEPTIONS]
                 [--EXPLAIN_TEMPLATE_LOADING] [--PREFERRED_URL_SCHEME]
                 [--JSON_AS_ASCII] [--JSON_SORT_KEYS]
                 [--JSONIFY_PRETTYPRINT_REGULAR] [--JSONIFY_MIMETYPE]
                 [--TEMPLATES_AUTO_RELOAD] [--MAX_COOKIE_SIZE]

optional arguments:
  -h, --help            show this help message and exit

default parameters:
  --ENV                 default is 'production'
  --DEBUG               default is False
  --TESTING             default is False
  --PROPAGATE_EXCEPTIONS
                        default is None
  --PRESERVE_CONTEXT_ON_EXCEPTION
                        default is None
  --SECRET_KEY          default is None
  --PERMANENT_SESSION_LIFETIME
                        default is datetime.timedelta(days=31)
  --USE_X_SENDFILE      default is False
  --SERVER_NAME         default is None
  --APPLICATION_ROOT    default is '/'
  --SESSION_COOKIE_NAME
                        default is 'session'
  --SESSION_COOKIE_DOMAIN
                        default is None
  --SESSION_COOKIE_PATH
                        default is None
  --SESSION_COOKIE_HTTPONLY
                        default is True
  --SESSION_COOKIE_SECURE
                        default is False
  --SESSION_COOKIE_SAMESITE
                        default is None
  --SESSION_REFRESH_EACH_REQUEST
                        default is True
  --MAX_CONTENT_LENGTH
                        default is None
  --SEND_FILE_MAX_AGE_DEFAULT
                        default is datetime.timedelta(seconds=43200)
  --TRAP_BAD_REQUEST_ERRORS
                        default is None
  --TRAP_HTTP_EXCEPTIONS
                        default is False
  --EXPLAIN_TEMPLATE_LOADING
                        default is False
  --PREFERRED_URL_SCHEME
                        default is 'http'
  --JSON_AS_ASCII       default is True
  --JSON_SORT_KEYS      default is True
  --JSONIFY_PRETTYPRINT_REGULAR
                        default is False
  --JSONIFY_MIMETYPE    default is 'application/json'
  --TEMPLATES_AUTO_RELOAD
                        default is None
  --MAX_COOKIE_SIZE     default is 4093
```

The `Multiplexor` constructor can take in a path to a config file, 
a config object (that subclasses a dictionary), or a string.

</p>
</details>

<details>
<summary>Convert from Argparse</summary>
<p>

It is very common to parse arguments with python's `argparse` 
and then pass the resulting `Namespace` as a parameter to a 
function or class. 

Here's a simple example. Say you have a calculator function like so:
```python
def calculator(value1, value2, operation):
    op = getattr(operator, operation)
    result = op(value1, value2)
    print(result)
```

A typical way to run this as a CLI is to define all argparse arguments 
and run calculator like so:

```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Simple Calculator CLI')
    parser.add_argument('operation', type=str, choices=['add', 'sub'],
                        help='what operation to perform')
    parser.add_argument('value1', type=float,
                        help='first value')
    parser.add_argument('value2', type=float,
                        help='second value')
    args = parser.parse_args()
    calculator(**vars(args))
```

_Note_: Notice that using getattr on operator might not be safe as the 
`operation` can be anything? This is fine because the `operation` is actually 
restricted to a few choices by argparse. 

With `multiplex` one can simply create a configuration 
file containing something like the following:

```yaml
argparse:
  parser:
    description: 'Simple Calculator CLI'
  arguments:
    - name_or_flags: operation
      choices: [add, sub]
      help: 'what operation to perform'
    - name_or_flags: value1
      type: float
      help: 'first value'
    - name_or_flags: value2
      type: float
      help: 'second value'

```

And replace the whole argparse CLI creation with an automated one:

```python
if __name__ == "__main__":
    from multiplex import Multiplexor

    m = Multiplexor('calculator.yaml')
    args = m.get_conf()
    calculator(**args.data)
```

With this in place, it is now much easier to extend the functionality of 
your calculator application, as any config changes will be mirrored in the CLI.
To add more operations, like say, multiplication and modulus, we can simply
change one line in `calculator.yaml`:

```yaml
choices: [add, sub, mul, mod]
```

</p>
</details>

<details>
<summary>Nested configuration files</summary>
<p>
More to come!
</p>
</details>

<details>
<summary>Multiple sub-programs</summary>
<p>
More to come!
</p>
</details>


You can view these examples in the [examples](examples) directory.  

## Changelog

* April 23, 2020:
    * Move argparse parser creation logic to [`ArgparseEngine`](multiplex/engines.py).
    * Add capabilities to create custom parser object as well, see the new calculator example.
* April 22, 2020: 
    * Add basic `setup.py` to enable local install of package. 
    To do this, run `pip3 install -e path/to/multiplex`. 
    * Change the examples accordingly, they now import from `multiplex` directly. 
    * Add `__init__.py` to enable simplified imports
(i.e: `from multiplex.parser import Multiplexor` is now `from multiplex import Multiplexor`) 
* April 16, 2020: Add flask example.
* April 14, 2020: Refactor codebase into `multiplex/config` and `multiplex/parser`, added calculator example.