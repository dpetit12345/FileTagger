import unittest
import sys

import Tagger
from Tagger import Tagger
from Tagger.Tagger import TestFunction

class Test_DirectoryTests(unittest.TestCase):
    def test_A(self):
        #self.fail("Not implemented")
        self.assertEqual(1,1)

    def test_B(self):
        self.assertEqual('Hello', TestFunction())

if __name__ == '__main__':
    unittest.main()
