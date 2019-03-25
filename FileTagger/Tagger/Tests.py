import unittest
import sys, os
from classical_fixes import listToString
from classical_fixes import makeKey
from classical_fixes import reverseName

sys.path.insert(0, os.path.dirname(__file__))

from Tagger import TestFunction

from Cluster import ClusterMaker

class Test_DirectoryTests(unittest.TestCase):
    def test_A(self):
        #self.fail("Not implemented")
        self.assertEqual(1,1)

    def test_B(self):
        self.assertEqual('Hello', TestFunction())


class Test_ClusteringTests(unittest.TestCase):
    def test_SingleFile(self):
        cm = ClusterMaker()
        paths = []
        dir_path = os.path.dirname(os.path.realpath(__file__))
        fullpath = os.path.join(dir_path, 'TestData\\file1.flac')
        paths.append(fullpath )
        cm.clusterFiles(paths)
        self.assertTrue(len(cm.clusters) == 1, 'file1.flac not cluster correctly')

    def test_SingleNonAudioFile(self):
        cm = ClusterMaker()
        paths = []
        dir_path = os.path.dirname(os.path.realpath(__file__))
        fullpath = os.path.join(dir_path, 'TestData\\fileisnotanaudiofile.txt')
        paths.append(fullpath )
        cm.clusterFiles(paths)
        self.assertTrue(len(cm.clusters) == 0, 'No audio file did not cluster correctly')

    def test_SingleBadFile(self):
        cm = ClusterMaker()
        paths = []
        dir_path = os.path.dirname(os.path.realpath(__file__))
        fullpath = os.path.join(dir_path, 'TestData\\nosuchfile.txt')
        paths.append(fullpath )
        cm.clusterFiles(paths)
        self.assertTrue(len(cm.clusters) == 0, 'None audio file did not cluster correctly')


    def test_MultipleFilesSameCluster(self):
        cm = ClusterMaker()
        paths = []
        dir_path = os.path.dirname(os.path.realpath(__file__))
        fullpath = os.path.join(dir_path, 'TestData\\file1.flac')
        paths.append(fullpath )
        fullpath = os.path.join(dir_path, 'TestData\\file2.flac')
        paths.append(fullpath )

        cm.clusterFiles(paths)
        self.assertTrue(len(cm.clusters) == 1, 'Sibling files did not cluster correctly')

    def test_MultipleFilesDifferentCluster(self):
        cm = ClusterMaker()
        paths = []
        dir_path = os.path.dirname(os.path.realpath(__file__))
        fullpath = os.path.join(dir_path, 'TestData\\file1.flac')
        paths.append(fullpath )
        fullpath = os.path.join(dir_path, 'TestData\\subfolder\\file2.flac')
        paths.append(fullpath )

        cm.clusterFiles(paths)
        self.assertTrue(len(cm.clusters) == 2, 'Multiple files did not cluster correctly')

    def test_SingleDirectoryNoRecursion(self):
        cm = ClusterMaker()
        paths = []
        dir_path = os.path.dirname(os.path.realpath(__file__))
        fullpath = os.path.join(dir_path, 'TestData')
        paths.append(fullpath )
        cm.clusterFiles(paths,recursive=False)
        self.assertTrue(len(cm.clusters) == 1, 'Non-recursive clustering incorrect')
    
    def test_SingleDirectoryWithRecursion(self):
        cm = ClusterMaker()
        paths = []
        dir_path = os.path.dirname(os.path.realpath(__file__))
        fullpath = os.path.join(dir_path, 'TestData')
        paths.append(fullpath )
        cm.clusterFiles(paths,recursive=True)
        self.assertTrue(len(cm.clusters) == 2, 'Recursive clustering incorrect')
        
    def test_MultiplePaths(self):
        cm = ClusterMaker()
        paths = []
        dir_path = os.path.dirname(os.path.realpath(__file__))
        fullpath = os.path.join(dir_path, 'TestData')
        paths.append(fullpath )
        fullpath = os.path.join(dir_path, 'TestData\\file1.flac')
        paths.append(fullpath )

        cm.clusterFiles(paths,recursive=False)
        self.assertTrue(len(cm.clusters) == 2, 'Multiple path clustering incorrect')

    def test_ListToString(self):
        mylist = ['Test1', 'Test2', 'Test3']
        self.assertEqual('Test1;Test2;Test3', listToString(mylist), 'List did not convert to string correctly.')
        another = [1,2,3]
        self.assertEqual('1;2;3', listToString(another), 'List did not convert to string correctly.')
        another = []
        self.assertEqual('', listToString(another), 'List did not convert to string correctly.')

    def test_ReverseName(self):
        #makeKey
        name = 'OneWord'
        self.assertEqual(reverseName(name),'OneWord', 'One word name not reversed correctly.')
        name = 'Two Words'
        self.assertEqual(reverseName(name),'Words, Two', 'Two word name not reversed correctly.')
        name = 'Now Three Words'
        self.assertEqual(reverseName(name),'Words, Now Three', 'Three word name not reversed correctly.')
        name = ''
        self.assertEqual(reverseName(name),'', 'Empty name not reversed correctly.')

    def test_TestMakeKey(self):
        name = 'Testing-/ This Name âéèçìíîñáàùúûýüĀ'
        self.assertEqual(makeKey(name),'testingthisnameaeeciiinaauuuyua','Incorrect key made')

if __name__ == '__main__':
    unittest.main()
