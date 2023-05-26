import sys


def dog():
    print('dog')


def main():
    if sys.argv[0] == 'dog':
        dog()


if __name__ == 'main':
    main()
