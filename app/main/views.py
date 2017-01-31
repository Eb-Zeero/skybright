from flask import request
from urllib.parse import urlparse
from flask import render_template, Flask
from bokeh.embed import autoload_server

BOKEH_PORT = 5100

from . import main


@main.route('/')
def index():
    up = urlparse(request.url)
    scheme = up.scheme
    host = up.netloc
    port = up.port
    if port:
        host = host[:-(len(str(port)) + 1)]
    bokeh_server_url = '{scheme}://{host}:{bokeh_port}'.format(scheme=scheme, host=host, bokeh_port=BOKEH_PORT)
    bokeh_script = autoload_server(None, app_path='/skybright', url=bokeh_server_url)
    return render_template('index.html', bokeh_script=bokeh_script)

@main.route('/what_is')
def what_is():
    return render_template('what_is.html')
