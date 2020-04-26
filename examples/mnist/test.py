# Inspired from https://github.com/pytorch/examples/blob/master/mnist/main.py

import argparse

import torch
import torch.nn.functional as F
from torchvision import datasets, transforms

from examples.mnist.utils import init_model
from multiplex import register_parser, register_entrypoint


def test(model, device, test_loader):
    model.eval()
    test_loss = 0
    correct = 0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += F.nll_loss(output, target, reduction='sum').item()  # sum up batch loss
            pred = output.argmax(dim=1, keepdim=True)  # get the index of the max log-probability
            correct += pred.eq(target.view_as(pred)).sum().item()

    test_loss /= len(test_loader.dataset)

    print('\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
        test_loss, correct, len(test_loader.dataset),
        100. * correct / len(test_loader.dataset)))


@register_parser
def get_parser(parents):
    parser = argparse.ArgumentParser(description='Testing tool for an MNIST network', parents=parents)
    parser.add_argument('--batch-size', type=int, default=1000, metavar='N',
                        help='input batch size for testing (default: 1000)')
    parser.add_argument('-f', '--from-save', type=str, dest='model_path', help='load model from save')
    return parser


@register_entrypoint
def main(args):
    model, device, use_cuda = init_model(args.seed, args.no_cuda)

    if args.model_path:
        state_dict = torch.load(args.model_path, map_location=device)
        model.load_state_dict(state_dict)
        print(f'Loaded model from {args.model_path}')

    kwargs = {'num_workers': 1, 'pin_memory': True} if use_cuda else {}
    test_loader = torch.utils.data.DataLoader(
        datasets.MNIST('../data', train=False, transform=transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,))
        ])),
        batch_size=args.batch_size, shuffle=True, **kwargs)
    test(model, device, test_loader)
