from unittest.mock import patch # allows us to mock the behaviour of the django get db function by simulating the db being available or not available when we test our command
from django.core.management import call_command # allows us to call our management command in our source code
from django.db.utils import OperationalError # this is the error that django throws when the db is unavailable. we will use this to simulate the db being available or not
from django.test import TestCase

class CommandsTestCase(TestCase):

    def test_wait_for_db_ready(self): # our management command will try to retrieve the db connection from django, when it does, it will check if it retrieves an operational error or not. if it didnt, the db is available and vice versa
        """Test waiting for db when it is available""" # to setup the test, we will override the behaviour of the connection handler and make it always return true without exception for this test

        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi: # the way that we test our db is by retrieving the db via the connection handler, the location of the code being called is in this module (django.db.utils.ConnectionHandler), and the function called when retrieving the db is __getitem__
            gi.return_value = True # an option in a mock object to mock the behavior of the function. So whenever the function above is called, instead of doing what it does, it will be overriden to this mock object
            # this also will monitor how many times the function we called
            call_command('wait_for_db') # this is the management command that we will create
            self.assertEqual(gi.call_count, 1) # check that __getitem__ was called only once. call_count is an option for mock objects


    @patch('time.sleep', return_value=True) # since the db will be checked every 1 second to see if its ready, this decorator is used here to speed up the test and remove the delay (we are mocking the delay by returning something immediately (true or None) as opposed to 'sleeping'). this decorator does the same as the patch command used earlier
    def test_wait_for_db(self, ts): # the patch decorator passes in an arguement (like gi in the previous test)
        """Test waiting for db 5 times with a success in 6th time"""

        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.side_effect = [OperationalError] * 5 + [True] # we will make it raise and OperationalError fives times, there is no reason for choosing 5 times, it could be anything
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 6)
