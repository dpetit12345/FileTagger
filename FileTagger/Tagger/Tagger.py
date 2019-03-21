import argparse

if __name__ == '__main__':
    #process the command like args
    parser = argparse.ArgumentParser(prog='Tagger', description='Process tags in all files in a given directory.')
    parser.add_argument('files', help='List of files or a directory', nargs='*')
    parser.add_argument('-r', action='store_true', help='Recursively find files in subdirectories')
    parser.add_argument('-noui', action='store_true', help='Run without GUI UI')
    parser.add_argument('-v', action='store', help='Verbosity 1=Error, 2=Warning, 3=Info',type=int,choices=[1,2,3])
    args = parser.parse_args()
    print(args.files)
    print(args)

def TestFunction():
    return 'Hello'