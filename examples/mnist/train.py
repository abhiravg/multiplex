# Inspired from https://github.com/pytorch/examples/blob/master/mnist/main.py

import torch
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
from torch.optim.lr_scheduler import StepLR
from multiplex import register_parser, register_entrypoint, Multiplexor

from examples.mnist.utils import init_model

app = Multiplexor(__file__)


def train(args, model, device, train_loader, optimizer, scheduler):
    for epoch in range(1, args.epochs + 1):
        print('Starting Epoch: {}'.format(epoch))
        train_epoch(args, model, device, train_loader, optimizer, epoch)
        scheduler.step()


def train_epoch(args, model, device, train_loader, optimizer, epoch):
    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = F.nll_loss(output, target)
        loss.backward()
        optimizer.step()
        if batch_idx % args.log_interval == 0:
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                epoch, batch_idx * len(data), len(train_loader.dataset),
                100. * batch_idx / len(train_loader), loss.item()))


@register_parser
def get_parser(parents):
    return app.get_parser(parents)


@register_entrypoint
def main(args):
    model, device, use_cuda = init_model(args.seed, args.no_cuda)
    kwargs = {'num_workers': 1, 'pin_memory': True} if use_cuda else {}
    train_loader = torch.utils.data.DataLoader(
        datasets.MNIST('../data', train=True, download=True,
                       transform=transforms.Compose([
                           transforms.ToTensor(),
                           transforms.Normalize((0.1307,), (0.3081,))
                       ])),
        batch_size=args.batch_size, shuffle=True, **kwargs)

    optimizer = optim.Adadelta(model.parameters(), lr=args.lr)
    scheduler = StepLR(optimizer, step_size=1, gamma=args.gamma)

    train(args, model, device, train_loader, optimizer, scheduler)

    if args.save_model:
        torch.save(model.state_dict(), "mnist_cnn.pt")
