import argparse
import sys
from Logging import Log
from Logging import LogLevel
from Cluster import ClusterMaker


if __name__ == '__main__':
    #process the command like args
    parser = argparse.ArgumentParser(prog='Tagger', description='Process tags in all files in a given directory.')
    parser.add_argument('files', help='List of files or a directory', nargs='*')
    parser.add_argument('-r', action='store_true', help='Recursively find files in subdirectories')
    parser.add_argument('-e', action='store_true', help='Enumerate clusters')
    parser.add_argument('-noui', action='store_true', help='Run without GUI UI')
    parser.add_argument('-v',default=2, action='store', help='Verbosity 1=Error, 2=Warning, 3=Info',type=int,choices=[1,2,3])
    args = parser.parse_args()
    
    #Log.writeLog(args.files, LogLevel.ERROR)
    #Log.writeLog(args, LogLevel.INFO)
    #Log.writeError('Test Error')
    #Log.writeInfo('Test Info')

    recursive = args.r
    useUI = not args.noui
    enum = args.e


    if args.noui and len(args.files) == 0:
        Log.writeError('No files specified and UI not active. Nothing to do.')
        quit()

    cm = ClusterMaker()
    
    Log.writeLog('Creating clusters for: ' + ', '.join(args.files), LogLevel.INFO)
    cm.clusterFiles(args.files, recursive)

    if len(cm.clusters) == 0:
        Log.writeError('Unable to cluster files. Nothing to do.')
        quit()


    if enum:
        Log.writeInfo ('Created %i clusters.' % len(cm.clusters))
        for i, (k, v) in enumerate(cm.clusters.items()):
            Log.writeLog('%i ' % (i + 1) + k + ': %i files' % len(v.files), LogLevel.INFO)



    

def TestFunction():
    return 'Hello'