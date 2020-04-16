import os
from os import path
import unittest
from datetime import datetime

from helper_classes.Logger import Logger

class TestLogger(unittest.TestCase):

    def setUp(self):
        self.log_path = "testing/unit/test_data/testLog.txt"
        self.logger = Logger(self.log_path)

    def test_writeToLog_no_time(self):
        # Arrange
        log_line = "Test line 1\nTest line 2\nTest line 3" 
        expected = log_line + "\n"

        # Act
        self.logger.writeToLog(log_line, False)

        # Assert
        self.assertFalse(self.isLogEmpty()) # Log shouldn't be empty

        with open(self.log_path, "r") as log_file:
            actual = log_file.read()

        self.assertEqual(expected, actual)

    def test_writeToLog_time(self):
        # Arrange
        log_line = "Test line 1\nTest line 2\nTest line 3 - Time = "
        expected = log_line

        # Act
        self.logger.writeToLog(log_line, True)

        # Assert
        self.assertFalse(self.isLogEmpty()) # Log shouldn't be empty

        with open(self.log_path, "r") as log_file:
            actual = log_file.read()     

        string_split = actual.split("=")
        actual_without_time =string_split[0] + "= "
        self.assertEqual(expected, actual_without_time)

        try:
            datetime.strptime(string_split[1][1:][:-1], "%d/%m/%Y, %H:%M:%S")
        except: # If exception raised, time didn't save correctly, so test fails
            self.assertTrue(False)
        else: # No exception means time saved correctly, so test passes
            self.assertTrue(True)
            
    def isLogEmpty(self):
        is_empty = False
        try:
            is_empty = os.stat(self.log_path).st_size == 0
        except:
            is_empty = not(path.exists(self.log_path))
        
        return is_empty

    def tearDown(self):
        # Delete logs created
        try:
            os.remove(self.log_path)
        except:
            pass