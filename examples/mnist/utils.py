import torch

from examples.mnist.models.convnet import Net


def init_model(seed=1, no_cuda=False):
    torch.manual_seed(seed)
    use_cuda = not no_cuda and torch.cuda.is_available()
    device = torch.device("cuda" if use_cuda else "cpu")
    model = Net().to(device)
    return model, device, use_cuda
