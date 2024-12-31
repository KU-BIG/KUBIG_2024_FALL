from config.args import parse_arguments
from training.trainer import train

if __name__ == "__main__":
    args = parse_arguments()
    train(args)
