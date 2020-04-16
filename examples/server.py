# Improved using multiplex (the path manipulation should be removed once
# multiplex is pip-installed, this ensures it uses the local copy)
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from multiplex.parser import Multiplexor

from flask import Flask

app = Flask(__name__)

m = Multiplexor(dict(app.config))
args = m.get_conf()
app.config.update(args.data)

print(dict(app.config))
