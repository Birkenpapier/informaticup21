# Execute this file to run the application 5 times in a row. There is a 5 minute delay between calls to connection.py.
# It finishes roughly after 25 minutes. The received JSON strings are saved to multiple files, named after the time
# they were received.

from datetime import datetime
import json
import os
import time
import sys

x = int(sys.argv[1])

for i in range(x):
    os.system('start /wait cmd /c "python connection.py"')
    time.sleep(1)