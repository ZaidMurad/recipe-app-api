import time # default python module, used to make our app sleep for delay
from django.db import connections # used to test if the db connection is available
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand # we need to build on it to create custom commands


class Command(BaseCommand):
    """Django command to pause execution until the db is available"""

    def handle(self, *args, **options): # must be called handle, it runs whenever we use our custom management command
        self.stdout.write('Waiting for database...') # used to print text to the screen
        db_conn = None # short for db connection
        while not db_conn: # means while its None or false
            try:
                db_conn = connections['default'] # try setting db_conn to the db connection
            except OperationalError: # if db is unavailable
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1) # sleep for one second before trying again

        self.stdout.write(self.style.SUCCESS('Database available!'))
