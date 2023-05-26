import sys


def dog():
    print('dog')


def cat():
    print('cat')


def main():
    if sys.argv[0] == 'cat':
        cat()
    else:
        dog()

if __name__ == 'main':
    main()
