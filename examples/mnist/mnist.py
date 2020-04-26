# Inspired from https://github.com/pytorch/examples/blob/master/mnist/main.py

from multiplex import Multiplexor, register_entrypoint


@register_entrypoint
def main(args):
    print('Welcome to the MNIST program!')
    print('This program currently can only train and test the network, please try those out.\n')


if __name__ == '__main__':
    m = Multiplexor('mnist.yaml')
    m.execute()
