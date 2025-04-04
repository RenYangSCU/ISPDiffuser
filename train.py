import argparse
import os
import random
import socket
import yaml
import torch
import torch.backends.cudnn as cudnn
import torch.utils.data
import numpy as np
import torchvision
import models
import datasets
import utils
from models.ISPDiffuser import ISPDiffuser


def parse_args_and_config():
    root_path = "/data/ISP/AAAI-25/ISPDiffuser_final_code"
    parser = argparse.ArgumentParser(description='ISP Diffusion Models')
    parser.add_argument("--config", default='configs/ZRR_dataset.yml', type=str,
                        help="Path to the config file")
    parser.add_argument('--mode', type=str, default='training', help='training or evaluation')
    parser.add_argument('--resume', default='', type=str,
                        help='Path for checkpoint to load and resume')
    parser.add_argument("--image_folder", default='results/', type=str,
                        help="Location to save restored validation image patches")
    parser.add_argument('--seed', default=230, type=int, metavar='N',
                        help='Seed for initializing training (default: 230)')
    args = parser.parse_args()

    with open(os.path.join(root_path, args.config), "r") as f:
        config = yaml.safe_load(f)
    new_config = dict2namespace(config)

    return args, new_config


def dict2namespace(config):
    namespace = argparse.Namespace()
    for key, value in config.items():
        if isinstance(value, dict):
            new_value = dict2namespace(value)
        else:
            new_value = value
        setattr(namespace, key, new_value)
    return namespace


def main():
    args, config = parse_args_and_config()
    # setup device to run
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    print("Using device: {}".format(device))
    config.device = device

    # set random seed
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.seed)
    torch.backends.cudnn.benchmark = True

    # data loading
    print("=> using dataset '{}'".format(config.data.train_dataset))
    DATASET = datasets.__dict__[config.data.type](config)

    # create model
    print("=> creating ISP diffusion model...")
    diffusion = ISPDiffuser(args, config)
    diffusion.train(DATASET)


if __name__ == "__main__":
    main()
