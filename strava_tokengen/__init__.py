#!/usr/bin/env python
# -*- coding: utf-8 -*-

from configparser import ConfigParser
import contextlib
import os
import textwrap

import cherrypy
from jinja2 import Environment, PackageLoader
from stravalib import Client


CONFIG_DIR = os.path.join(os.environ['HOME'], '.config')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'strava-tokengen.conf')


class StravaTokenGen(object):

    def __init__(self, *args, **kwargs):
        """Create the webapp and load the template environment"""
        super().__init__(*args, **kwargs)

        self.env = Environment(
            loader=PackageLoader('strava_tokengen', 'templates'),
            autoescape=False
        )

    @property
    def client_id(self):
        return cherrypy.request.app.config['strava']['client_id']

    @property
    def client_secret(self):
        return cherrypy.request.app.config['strava']['client_secret']

    @property
    def redirect_uri(self):
        return cherrypy.request.app.config['strava']['redirect_uri']

    @cherrypy.expose
    def index(self):
        """Main page"""
        auth_url = Client().authorization_url(scope="view_private,write",
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
    config = ConfigParser()
    config['global'] = {
        'environment': '"production"',
        'log.screen': True,
        'server.socket_host': '"localhost"',
        'server.socket_port': 5000,
    }
    config['strava'] = {
        'client_id': '""',
        'client_secret': '""',
        'redirect_uri': '"http://localhost:5000/auth"',
    }
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        config.write(f)


def run_server():
    """Create a default config file if one doesn't exist and run the server"""
    config = ConfigParser()
    try:
        with open(CONFIG_FILE, 'r') as f:
            config.read_file(f)
    except FileNotFoundError:
        msg = "WARNING: Creating the default config file at '{}'. You will "\
              "need to set the 'client_id', 'client_secret', and "\
              "'redirect_uri' values before this application will work "\
              "properly".format(CONFIG_FILE)
        print(textwrap.fill(msg, width=90, subsequent_indent="         "))

        create_default_config()
        return

    missing = [x for x in ('client_id', 'client_secret', 'redirect_uri')
               if not config.get('strava', x, fallback="").strip("\"'")]
    for x in missing:
        print("ERROR: Couldn't find the required config value '{}'".format(x))
    if missing:
        print()
        print("Fill in the missing values before running the application")
        return

    cherrypy.quickstart(StravaTokenGen(), '/', config=CONFIG_FILE)

if __name__ == "__main__":
    run_server()
