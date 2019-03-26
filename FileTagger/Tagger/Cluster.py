from os import listdir
from os.path import isfile, join
import glob
import os
import mutagen
import pprint
import unicodedata
import copy
import dictdiffer
from Logging import Log
from Logging import LogLevel

from mutagen.flac import FLAC

class AudioFile():
    def __init__(self, audio):
        self.orig = copy.deepcopy(audio)
        self.audio = audio
    def getDiffs(self):
        return list(dictdiffer.diff(self.orig.tags.items(),self.audio.tags.items()))

class Cluster():
    """Represents a cluster of files, meaning they belong to the same album"""
    def __init__(self):
        self.files = []

    def addFile(self, audio):
        self.files.append(audio)

class ClusterMaker():
    def __init__(self):
        self.clusters = {}

    def clusterFiles(self, paths, recursive=True):
        for path in paths:
            self.addFiles(path, recursive)
        
    def addFiles(self, path, recursive):
        #uses path to load a bunch of mutagen clusters keyed by shared directory.
        
        justfiles = []

        #the path could be a file or a directory
        if os.path.isfile(path):
            justfiles.append(path)

        else:
            files = glob.glob(path + '/**/*.*', recursive=recursive)
            justfiles = [f for f in files if isfile(f)]

        for file in justfiles:
            filepath = os.path.dirname(file)
            #audio = FLAC(file)
            audio = mutagen.File(file)

            if audio is not None:
                afile = AudioFile(audio)
                #print(filepath)
                if filepath in self.clusters:
                    #print('E-' + file)
                    self.clusters[filepath].addFile(afile)
                else:
                    #print('A-' + file)
                    self.clusters[filepath] = Cluster()
                    self.clusters[filepath].addFile(afile)
            else:
                Log.writeInfo('bad file: ' + file)





        



