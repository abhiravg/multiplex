# Improved using multiplex
from multiplex import Multiplexor

from flask import Flask

app = Flask(__name__)

m = Multiplexor(dict(app.config))
args = m.get_conf()
app.config.update(args.data)

print(dict(app.config))
