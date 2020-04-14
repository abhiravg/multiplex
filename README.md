# Multiplex: Simple, elegant and composable configurations.

This library relies on [argparse](https://docs.python.org/3.8/library/argparse.html) 
and [configurator](https://configurator.readthedocs.io/en/latest/index.html) in order to 
bring you command line interfaces (CLIs) that are dynamically created, with arguments that are 
automatically parsed and merged with any default configurations the program may have. The result 
is a well-structured config object that can be used in a wide range of applications.

## Simple Use Cases

#### CLI from config file

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
    from multiplex.parser import Multiplexor

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

You can view this toy example in the [examples](examples/calculator.py) directory.  

## Changelog

* April 14, 2020: Refactored codebase into `multiplex/config` and `multiplex/parser`, added calculator example.