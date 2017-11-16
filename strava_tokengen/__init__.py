#!/usr/bin/env python
# -*- coding: utf-8 -*-

from configparser import ConfigParser
import contextlib
import os
import textwrap
from urllib.parse import urlparse

import cherrypy
from jinja2 import Environment, PackageLoader
import pkg_resources
from stravalib import Client


CONFIG_DIR = os.environ.get('XDG_CONFIG_HOME', os.path.join(os.environ['HOME'], '.config'))
CONFIG_FILE = os.path.join(CONFIG_DIR, 'strava-tokengen.conf')


class StravaTokenGen(object):

    def __init__(self, *, client_id, client_secret, redirect_uri, scope):
        """Create the webapp and load the template environment"""
        super().__init__()

        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope
        self.env = Environment(
            loader=PackageLoader(__name__, 'templates'),
            autoescape=False
        )

    @cherrypy.expose
    def index(self):
        """Main page"""
        auth_url = Client().authorization_url(scope=self.scope,
                                              client_id=self.client_id,
                                              redirect_uri=self.redirect_uri)
        return self.env.get_template('index.html').render(auth_url=auth_url)

    @cherrypy.expose
    def auth(self, code=None, error=None, **_):
        """Handle the auth callback from Strava"""
        if error or not code:
            if not code:
                msg = "No authorization code recieved from Strava"
            else:
                msg = "Error"
            if error:
                msg = "{}: {}".format(msg, error)
            return self.env.get_template('error.html').render(msg=msg)

        token = Client().exchange_code_for_token(code=code,
                                                 client_id=self.client_id,
                                                 client_secret=self.client_secret)
        return self.env.get_template('result.html').render(token=token)


def create_default_config():
    """Create a default config file template"""
    conf = pkg_resources.resource_string(__name__, "strava-tokengen.conf")
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, 'wb') as f:
            f.write(conf)
    except OSError:
        msg = "ERROR: Failed to create the config file template - create it "\
              "manually with the following contents:"
        print(textwrap.fill(msg, width=90, subsequent_indent="       "))
        print("{1}\n{0}\n{1}".format(conf.decode('utf-8'), '-'*60))


def validate_config(conf):
    """Ensure the config is properly filled out (raises ValueError if not)"""
    if 'scope' not in conf or \
            any(not conf.get(x)
                for x in ('client_id', 'client_secret', 'redirect_uri')):
        raise ValueError("Not all required config parameters are set - check "
                         "the config file")


def run_server():
    """Create a default config file if one doesn't exist and run the server"""
    conf_parser = ConfigParser()
    try:
        with open(CONFIG_FILE, 'r') as f:
            conf_parser.read_file(f)
    except FileNotFoundError:
        msg = "WARNING: Creating the config file template at '{}'. You will "\
              "need to modify it before this application will work properly."\
              "".format(CONFIG_FILE)
        print(textwrap.fill(msg, width=90, subsequent_indent="         "))

        create_default_config()
        return

    tg_conf = conf_parser['strava-tokengen']
    validate_config(tg_conf)

    uri_data = urlparse(tg_conf['redirect_uri'])
    cherrypy.config.update({
        'environment': 'production',
        'log.screen': True,
        'server.socket_host': uri_data.hostname,
        'server.socket_port': uri_data.port
    })

    static_dir = pkg_resources.resource_filename(__name__, "static")
    config = {
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': static_dir,
            'tools.gzip.on': True,
        }
    }

    cherrypy.tree.mount(StravaTokenGen(**tg_conf), '/', config=config)
    cherrypy.engine.start()
    cherrypy.engine.block()
