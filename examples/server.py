from flask import Flask

from multiplex import Multiplexor

app = Flask(__name__)

m = Multiplexor(dict(app.config))
args = m.get_conf()
app.config.update(args.data)

print(dict(app.config))
