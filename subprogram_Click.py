import click
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from multiplex.parser import Multiplexor

program_folder = os.path.join(os.getcwd(), 'examples') 
print(program_folder)

class CLI(click.MultiCommand):

    def list_commands(self, ctx):
        rv = []
        for program_name in os.listdir(program_folder):
            if program_name.endswith('.py'):
                rv.append(program_name[:-3])
        rv.sort
        return rv

    def get_command(self, ctx, name):
        ns = {}
        fn = os.path.join(program_folder, name + '.py')
        with open(fn) as f:
            code = compile(f.read(), fn, 'exec')
            eval(code, ns,ns)
        return ns['cli']

cli = CLI(help = 'This tool\'s subprograms are loaded from the path dynamically')

if __name__ == "__main__":
    cli = cli()
    cli.list_commands()

    

