#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Classical Fixes
# Copyright (C) 2019 Dan Petit
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

#PLUGIN_NAME = 'Classical Fixes'
#PLUGIN_AUTHOR = 'Dan Petit'
#PLUGIN_DESCRIPTION = '''
#Fix items associated with classical music.


#PLUGIN_VERSION = '1.0'
#PLUGIN_API_VERSIONS = ['2.0']
#PLUGIN_LICENSE = 'GPL-3.0'
#PLUGIN_LICENSE_URL = 'https://www.gnu.org/licenses/gpl.txt'

#from picard import log
#from picard.cluster import Cluster
#from picard.album import Album
#from picard.ui.itemviews import BaseAction, register_cluster_action, register_album_action, register_clusterlist_action, register_file_action, register_track_action
#import suffixtree

import re
import os
import unicodedata
import mutagen
from Logging import Log
from Logging import LogLevel
from Cluster import Cluster

def makeKey(inputstring):
    stripped = ''.join(c for c in unicodedata.normalize('NFD', inputstring)
                  if unicodedata.category(c) != 'Mn')
    stripped = stripped.replace('-','')
    stripped = stripped.replace(' ','')
    stripped = stripped.replace('/','')
    stripped = stripped.replace('.','')
    stripped = stripped.replace("'",'')
    stripped = stripped.replace(',','')
    return stripped.lower()
    
def reverseName(inputString):
    nameOut = inputString.strip()
    lastSpace = nameOut.rfind(' ')
    if lastSpace == -1:
        return nameOut
    return nameOut[lastSpace+1:100] + ', ' + nameOut[0:lastSpace]

def listToString(list):
    return ';'.join(str(x) for x in list)
        

#TODO: Validate subgenres against this list
#ACCEPTABLE_SUBGENRES = {'Concerto', 'Orchestral', 'Opera', 'Chamber Music', 'Vocal', 'Choral', 'Solo', 'Symphonic'}
ORCH_RE = re.compile('[Oo]rchestr|[Oo]rkest|[Pp]hilharmoni|[Cc]onsort|[Ee]nsemb')
# DATE1_RE = re.compile('([0-9]{4})[ .\\-/][0-9]{1,2}[ .\\-/][0-9]{1,2}')
# DATE2_RE = re.compile('[0-9]{1,2}[ .\\-/][0-9]{1,2}[ .\\-/]([0-9]{4})')
#BRACKET_RE = re.compile('\\[(?![Ll][Ii][Vv][Ee]|[Bb][Oo][Oo]|[Ii][Mm]|[Ff][Ll][Aa][Cc]|[[Dd][Ss][Dd]|[Mm][Pp][3]|[Dd][Ss][Ff])[a-zA-Z0-9]{1,}\\]')
#\[(?![Ll][Ii][Vv][Ee]|[Bb][Oo][Oo]|[Ii][Mm]|[Ff][Ll][Aa][Cc]|[[Dd][Ss][Dd]|[Mm][Pp][3]|[Dd][Ss][Ff])[a-zA-Z0-9]{1,}\]

#class AlbumAction(BaseAction):
#    NAME = 'Menu for AlbumAction'

#    def callback(self, objs):
#        Log.writeInfo('AlbumAction called.')

#class TrackAction(BaseAction):
#    NAME = 'Menu for TrackAction'

#    def callback(self, objs):
#        Log.writeInfo('TrackAction called.')

#class ClusterListAction(BaseAction):
#    NAME = 'Menu for ClusterListAction'

#    def callback(self, objs):
#        Log.writeInfo('ClusterListAction called.')

#class FileAction(BaseAction):
#    NAME = 'Menu for FileAction'

#    def callback(self, objs):
#        Log.writeInfo('FileAction called.')        

class ArtistLookup():
    key=''
    name=''
    dates=''
    sortorder=''
    sortorderwithdates=''
    primaryrole=''
    primaryepoque =''

    def __init__ (self, line):
        lineparts = line.split('|')
        self.key=lineparts[0].strip()
        self.name=lineparts[1].strip()
        self.dates=lineparts[3].strip()
        self.sortorder=lineparts[2].strip()
        self.sortorderwithdates=lineparts[4].strip()
        self.primaryrole=lineparts[5].strip()
        self.primaryepoque=lineparts[6].strip()

class ClassicalFixes():
    
    def processFiles(self, clusters):
        Log.writeInfo('Classical Fixes started')

        regexes = [
            ['\\b[Nn][Uu][Mm][Bb][Ee][Rr][ ]*([0-9])','#\\1'],  #Replace "Number 93" with #93
            ['\\b[Nn][Oo][.]?[ ]*([0-9])','#\\1'], #No. 99 -> #99
            ['\\b[Nn][Rr][.]?[ ]*([0-9])','#\\1'], #Nr. 99 -> #99
            ['\\b[Nn][Bb][Rr][.]?\\s([0-9])', '#\\1'], #Nbr. 99 -> #99
            ['\\b[Oo][Pp][Uu][Ss][ ]*([0-9])','Op. \\1'], #Opus 99 -> Op. 99
			['\\b[Oo][Pp][.]?[ ]*([0-9])','Op. \\1'], #OP.   99 -> Op. 99
            ['\\b[Ss][Yy][Mm][ |.][ ]*([0-9])','Symphony \\1'], #Sym. -> Symphony
            ['\\b[Ss][Yy][Mm][Pp][Hh][Oo][Nn][Ii][Ee][ ]*[#]?([0-9])','Symphony #\\1'],  #Symphonie -> symphony
            ['\\b[Mm][Ii][Nn][.]','min.'],
            ['\\b[Mm][Aa][Jj][.]','Maj.'],
            ['\\b[Mm][Ii][Nn][Ee][Uu][Rr]\\b','min.'],
            ['\\b[Mm][Aa][Jj][Ee][Uu][Rr]\\b', 'Maj.'],
            ['\\b[Mm][Aa][Jj][Ee][Uu][Rr]\\b', 'Maj.'],
            ['\\b[Bb][. ]*[Ww][. ]*[Vv][. #]*([0-9])', 'BWV \\1'],
            ['\\b[Hh][. ]*[Ww][. ]*[Vv][. #]*([0-9])', 'HWV \\1'],
            ['\\b[Hh][ .]?[Oo]?[. ]?[Bb]?[ .]{1,}([XxVvIi]{1,}[Aa]?)', 'Hob. \\1'],
            ['\\b[Kk][ .]*([0-9])', 'K. \\1'],
            ['\\b[Aa][Nn][Hh][ .]*([0-9])', 'Anh. \\1'],
            ['[,]([^ ])', ', \\1'],
            ['\\s{2,}',' ']
        ]

        
        Log.writeInfo('Reading lookup File')

        Log.writeInfo('Script path: ' + os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.dirname(os.path.abspath(__file__)) + '/Data/artists.csv'
        if os.path.exists(filepath):
            Log.writeInfo('File exists')
            try:
                with open(filepath, 'r', encoding='utf-8') as artistfile:
                    artistlines = artistfile.readlines()
                Log.writeInfo('File read successfully')
            except:
                Log.writeError('Error opening artists file')
                return 1
        else:
            Log.writeError('Data file does not exist')
            return 1


        #populate the lookup
        artistLookup = {} #dictionary of artists in the lookup table
        for artistline in artistlines:
            art = ArtistLookup(artistline)
            artistLookup[art.key] = art
        
        #go through the track in the cluster        
        for ci, (ck, cluster) in enumerate(clusters.items()):
            #if not isinstance(cluster, Cluster) or not cluster.files:
            #    continue

            for i, f in enumerate(cluster.files):
                conductorTag=''               
                orchestraTag=''

                composerViewList=[]
                composerList=[]
                trackArtistList = []
                trackAlbumArtistList = []
                #normalize album artist list
                if 'albumartist' in f:
                    f['album artist'] = f['albumartist']
                else:
                    if 'album artist' in f:
                        f['albumartist'] = f['album artist']
                
                #album artist is string with semicolons, rest are lists
                #TODO: Pickup here
                        
               
                #fill the vars from the tags. Orchestra and conductor are assumed to be singular
                if 'conductor' in f:
                    conductorTag = listToString(f['conductor'])
                if 'orchestra' in f:
                    orchestraTag = listToString(f['orchestra'])
                if 'composer' in f:
                    composerList = f['composer']
                if 'composer view' in f:
                    composerViewList = f['composer view']
                if 'artist' in f:
                    trackArtistList = f['artist']
                if 'albumartist' in f:
                    #Log.writeInfo('Have albumartist: ' + listToString(f['albumartist']))
                    trackAlbumArtistList= f['albumartist']
                if 'album artist' in f:
                    #Log.writeInfo('Have album artist: ' + listToString(f['album artist']))
                    if set(trackAlbumArtistList) == set(f['album artist']):
                        Log.writeInfo('Have album artist: ' + listToString(f['album artist']) + ' same as albumartist tag') 
                        pass
                    else:
                        trackAlbumArtistList= f['album artist']                                          

                
                #if there is no orchestra tag, go through the artists and see if there is one that matches the orchestra list
                Log.writeInfo('Checking artists to fill conductor, composer, and orchestra tags if needed.')
                for trackArtist in trackArtistList:
                    trackArtistKey = makeKey(trackArtist)
                    if trackArtistKey in artistLookup:
                        foundArtist = artistLookup[trackArtistKey]
                        #Log.writeInfo ('Found track artist ' + trackArtist + ' in lookup list. Role is ' + foundArtist.primaryrole)
                        if foundArtist.primaryrole =='Orchestra' and not orchestraTag:
                            f['orchestra'] = foundArtist.name    
                            orchestraTag = foundArtist.name
                        if foundArtist.primaryrole =='Conductor' and not conductorTag:
                            f['conductor'] = foundArtist.name    
                            conductorTag = foundArtist.name
                        if foundArtist.primaryrole =='Composer' and not composerList:                          
                            f['composer'] = foundArtist.name
                            composerList = foundArtist.name
                            f['composer view'] = foundArtist.sortorderwithdates
                    else:
                        Log.writeInfo('No artists found for key: ' + trackArtistKey)

                Log.writeInfo('Checking album artists to fill conductor, composer, and orchestra tags if needed.')

                #Log.writeInfo('Track artists count: ' + len(trackAlbumArtistList))
                for albumArtist in trackAlbumArtistList:
                    trackAlbumArtistKey = makeKey(albumArtist)
                    if trackAlbumArtistKey in artistLookup:
                        foundArtist = artistLookup[trackAlbumArtistKey]
                        #Log.writeInfo ('Found track artist ' + trackArtist + ' in lookup list. Role is ' + foundArtist.primaryrole)
                        if foundArtist.primaryrole =='Orchestra' and not orchestraTag:
                            f['orchestra'] = foundArtist.name    
                            orchestraTag = foundArtist.name
                        if foundArtist.primaryrole =='Conductor' and not conductorTag:
                            f['conductor'] = foundArtist.name    
                            conductorTag = foundArtist.name
                        if foundArtist.primaryrole =='Composer' and not composerList:                          
                            f['composer'] = foundArtist.name
                            composerList = foundArtist.name
                            f['composer view'] = foundArtist.sortorderwithdates
                    else:
                        Log.writeInfo('No artists found for key: ' + trackArtistKey)

                
                #if there is a composer, look it up against the list and replace what is there if it is different.
                #same with view.
                Log.writeInfo('Looking up composer')
                if composerList:

                    newCompList = []
                    newCompViewList = []
                    epoque = ''
                    if 'epoque' in f:
                        epoque = f['epoque']

                    for composer in composerList:
                        #Log.writeInfo('There is a composer: ' + composerList)
                        composerKey = makeKey(composer)
                        #Log.writeInfo('Composerkey: ' + composerKey)
                        if composerKey in artistLookup:
                            foundComposer = artistLookup[composerKey]
                            if foundComposer.primaryrole == 'Composer':
                                Log.writeInfo('found a composer - setting tags')
                                #Log.writeInfo('existing Composer: |' + f['Composer'] + '| - composer: |' + f['composer'] + '|')
                                #Log.writeInfo('existing Composer View: |' + f['Composer View'] + '| - composer view: |' + f['composer view'] + '|')
                                newCompList.append(foundComposer.name)
                                #f['composer'] = foundComposer.name
                                newCompViewList.append(foundComposer.sortorderwithdates)
                                #f['composer view'].append(foundComposer.sortorderwithdates)
                                if foundComposer.primaryepoque:
                                    f['epoque'] = foundComposer.primaryepoque
     
                        else:
                            #use the actual name and derive the view
                            newCompList.append(composer)
                            newCompViewList.append(reverseName(composer))
                    f['composer'] = newCompList
                    f['composer view'] = newCompViewList

                #if there is no orchestra, but there is an artist tag that contains a name that looks like and orchestra, use that
                if 'orchestra' not in f:
                    for artist in trackArtistList:
                        if ORCH_RE.search(artist):
                            f['orchestra'] = artist
                            break

                Log.writeInfo('checking for conductor and orchestra in album artists')
                #if there is a conductor AND and orchestra tag, and they are both in the album artist tag, rearrange
                if 'conductor' in f and 'orchestra' in f:
                    Log.writeInfo('There is a conductor and orchestra tag')
                    foundConductor = False
                    foundOrchestra = False
                    #Log.writeInfo('Track artists count: ' + len(trackAlbumArtistList))
                    for artist in trackAlbumArtistList:
                        Log.writeInfo('Processing album artist: ' + artist + ' - conductor is: ' + listToString(f['conductor']) + ' - orchestra is: ' + listToString(f['orchestra']))
                        if artist in f['conductor']:
                            Log.writeInfo('Found Conductor in album artist')
                            foundConductor=True
                        if artist in f['orchestra']:
                            Log.writeInfo('Found orchestra in album artist')
                            foundOrchestra=True
                    if foundConductor or foundOrchestra:
                        newAlbumArtistList = []
                        if foundConductor:
                            newAlbumArtistList += f['conductor']
                        if foundOrchestra:
                            newAlbumArtistList += f['orchestra']
                        for artist in trackAlbumArtistList:
                            if artist not in f['conductor'] and artist not in f['orchestra']:
                                newAlbumArtistList.append(artist)

                        Log.writeInfo('Setting album artist to: ' + listToString(newAlbumArtistList))
                        if set(f['albumartist']) != set(newAlbumArtistList):
                            f['albumartist'] = newAlbumArtistList

                #TODO: Copy the above
                #Log.writeInfo('checking for conductor and orchestra in artists')
                ##if there is a conductor AND and orchestra tag, and they are both in the album artist tag, rearrange
                #if 'conductor' in f and 'orchestra' in f:
                #    Log.writeInfo('There is a conductor and orchestra tag')
                #    foundConductor = False
                #    foundOrchestra = False
                #    #Log.writeInfo('Track artists count: ' + len(trackAlbumArtistList))
                #    for artist in trackArtistList:
                #        Log.writeInfo('Processing artist: ' + artist + ' - conductor is: ' + f['conductor'])
                #        if artist == f['conductor']:
                #            Log.writeInfo('Found Conductor in album artist')
                #            foundConductor=True
                #        if artist == f['orchestra']:
                #            Log.writeInfo('Found orchestra in album artist')
                #            foundOrchestra=True
                #    if foundConductor and foundOrchestra:
                #        newArtistTag = ''
                #        newArtistTag = f['conductor'] + '; ' + f['orchestra'] + '; '
                #        for artist in trackArtistList:
                #            if artist != f['conductor'] and artist!=f['orchestra']:
                #                newArtistTag=newArtistTag+artist + '; '
                #            Log.writeInfo('Setting artist to: ' + newArtistTag[:-2] + '|')
                #            if f['artist'] != newArtistTag[:-2]:
                #                f['artist'] = newArtistTag[:-2]
                                


                Log.writeInfo('Reloading albumartist: ' + f['albumartist'])
                albumArtistsTag = f['albumartist']
                albumArtistsTag = albumArtistsTag.replace('; ',';')
                trackAlbumArtistList = albumArtistsTag.split(';')

                artistsTag = f['artist']
                artistsTag = artistsTag.replace('; ',';')
                trackArtistList = artistsTag.split(';')


                #At this point if there is no composer, but we find what look like a composer in the tags, move it
                if 'composer' not in f:
                    for artist in trackArtistList:
                        key = makeKey(artist)
                        if key in artistLookup:
                            foundComposer = artistLookup[key]
                            if foundComposer.primaryrole == 'Composer':
                                Log.writeInfo('Found composer ' + foundComposer.name + ' in track artist - moving')
                                f['composer'] = foundComposer.name
                                break

                if 'composer' not in f:
                    for artist in trackAlbumArtistList:
                        key = makeKey(artist)
                        if key in artistLookup:
                            foundComposer = artistLookup[key]
                            if foundComposer.primaryrole == 'Composer':
                                Log.writeInfo('Found composer ' + foundComposer.name + ' in track artist - moving')
                                f['composer'] = foundComposer.name
                                break

                Log.writeInfo('Before - albumartist is: ' + f['albumartist'] + '|')

                #if there is a composer tag, and it also exists in track or album artists, remove it.
                if 'composer' in f:
                    Log.writeInfo('Searching for composer in artist and album artist tags')
                    newArtists = ''
                    newAlbumArtistTag = ''
                    for artist in trackArtistList:
                        if artist.strip() != f['composer'].strip():
                            newArtists = newArtists + artist + '; '
                    if newArtists:
                        if f['artist'] != newArtists[:-2]:
                            f['artist'] = newArtists[:-2]
                    for albumArtist in trackAlbumArtistList:
                        if albumArtist.strip() != f['composer'].strip():
                            newAlbumArtistTag = newAlbumArtistTag + albumArtist + '; '
                    if newAlbumArtistTag:
                        f['albumartist'] = newAlbumArtistTag[:-2]

                Log.writeInfo('After - albumartist is: ' + f['albumartist'] + '|')


                #remove [] in album title, except for live, bootleg, flac*, mp3* dsd* dsf* and [import]
                f['album'] = re.sub('\\[(?![Ll][Ii][Vv][Ee]|[Bb][Oo][Oo]|[Ii][Mm]|[Ff][Ll][Aa][Cc]|[[Dd][Ss][Dd]|[Mm][Pp][3]|[Dd][Ss][Ff])[a-zA-Z0-9]{1,}\\]', '',  f['album'])

                #regexes for title and album name
                Log.writeInfo('Executing regex substitutions')
                for regex in regexes:
                    #Log.writeInfo(regex[0] + ' - ' + regex[1]) 
                    trackName = f['title']
                    albumName = f['album']
                    #Log.writeInfo('Was: ' + trackName + ' | ' + albumName)
                    trackName = re.sub(regex[0], regex[1], trackName)
                    albumName = re.sub(regex[0], regex[1], albumName)
                    #Log.writeInfo('Is now: ' + trackName + ' | ' + albumName)
                    f['title'] = trackName
                    f['album'] = albumName


                Log.writeInfo('Fixing genre')
                #move genre tag to "OrigGenre" and replace with Classical
                if 'genre' in f:
                    if f['genre'] != 'Classical':
                        f['origgenre'] = f['genre']

                f['genre'] = 'Classical'
                
              

        #cluster.update()


