import subprocess
from datetime import datetime
from os import path, chdir
import subprocess


basepath = path.dirname(__file__)


def take_note(text):
    filepath = path.abspath(path.join(basepath, "..", "..", "..", "Users", "Eric", "Desktop", "Notes"))

    chdir(filepath)

    _time = str(datetime.now().time()).replace(':', '-').split('.')[0]
    _date = str(datetime.now().date())

    filename = f'{_date}-{_time}.note'

    with open(filename, 'w') as f:
        f.write(text)
        
        f.close()
    
    subprocess.Popen(['notepad.exe', filename])
