import sys


def cat():
    print('cat')


def main():
    if sys.argv[0] == 'cat':
        cat()


if __name__ == 'main':
    main()
