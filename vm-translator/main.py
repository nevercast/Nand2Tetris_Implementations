""" VM Translator """
from optparse import OptionParser

import parse



def main():
    """ Entry point """
    opt_parser = OptionParser(usage="Usage: %prog [options] INPUT [OUTPUT]")
    opt_parser.add_option('-i', '--input', dest='input',
                          help="VM file to translate")
    # opt_parser.add_option('-o', )


if __name__ == "__main__":
    main()