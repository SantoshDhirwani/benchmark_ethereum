from __future__ import print_function
from argparse import ArgumentParser


def main():
    parser = ArgumentParser(
        description="It's a script to create Virtual machines "
            "and  install Ethereum in them."
    )
    parser.add_argument(
        '--nodes',
        type=int,
        required=True,
        help='Number of nodes',
        # default=1, # you can also add some default value, if you need
    )

    args = parser.parse_args()

    # use args.nodes as you need
    print(args.nodes)


if __name__ == '__main__':
    main()
