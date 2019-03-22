import argparse

from Logging import Log
from Logging import LogLevel
from Cluster import ClusterMaker


if __name__ == '__main__':
    #process the command like args
    parser = argparse.ArgumentParser(prog='Tagger', description='Process tags in all files in a given directory.')
    parser.add_argument('files', help='List of files or a directory', nargs='*')
    parser.add_argument('-r', action='store_true', help='Recursively find files in subdirectories')
    parser.add_argument('-noui', action='store_true', help='Run without GUI UI')
    parser.add_argument('-v',default=2, action='store', help='Verbosity 1=Error, 2=Warning, 3=Info',type=int,choices=[1,2,3])
    args = parser.parse_args()
    
    Log.writeLog(args.files, LogLevel.ERROR)
    Log.writeLog(args, LogLevel.INFO)
    Log.writeError('Test Error')
    Log.writeInfo('Test Info')

    cm = ClusterMaker()
    cm.clusterFiles(args.files)

    Log.writeInfo ('Created %i clusters.' % len(cm.clusters))
    for i, (k, v) in enumerate(cm.clusters.items()):
        Log.writeLog('%i' % i + k + '%i' % len(v.files), LogLevel.INFO)


def TestFunction():
    return 'Hello'