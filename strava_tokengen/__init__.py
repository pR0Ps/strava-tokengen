#!/usr/bin/env python
# -*- coding: utf-8 -*-

from configparser import ConfigParser
import os
import textwrap

import cherrypy
from jinja2 import Environment, PackageLoader
import pkg_resources
from stravalib import Client


__all__ = ["ConfigError", "run_server"]


CONFIG_DIR = os.environ.get('XDG_CONFIG_HOME', os.path.join(os.environ['HOME'], '.config'))
CONFIG_FILE = os.path.join(CONFIG_DIR, 'strava-tokengen.conf')


class ConfigError(ValueError):
    pass


class StravaTokenGen(object):

    def __init__(self, callback_domain):
        """Create the webapp and load the template environment"""
        super().__init__()

        self.callback_domain = callback_domain
        self.env = Environment(
            loader=PackageLoader(__name__, 'templates'),
            autoescape=False
        )

    @cherrypy.expose
    def index(self):
        """Main page"""
        return self.env.get_template('index.html').render(domain=self.callback_domain)

    @cherrypy.expose
    def connect(self, scope, client_id, client_secret, **_):
        """Store OAuth values on the session and redirect to the auth url"""
        cherrypy.session['scope'] = scope
        cherrypy.session['client_id'] = client_id
        cherrypy.session['client_secret'] = client_secret

        # Validate inputs
        if not all((scope, client_id, client_secret)):
            raise cherrypy.HTTPRedirect("/")

        redirect_uri = "http://{}/auth".format(self.callback_domain)
        auth_url = Client().authorization_url(scope=scope,
                                              client_id=client_id,
                                              redirect_uri=redirect_uri)
        raise cherrypy.HTTPRedirect(auth_url)

    @cherrypy.expose
    def auth(self, code=None, error=None, **_):
        """Handle the auth callback from Strava"""
        scope = cherrypy.session.get('scope')
        client_id = cherrypy.session.get('client_id')
        client_secret = cherrypy.session.get('client_secret')

        # Protect against invalid session
        if None in (scope, client_id, client_secret):
            raise cherrypy.HTTPRedirect("/")

        # Bad response from Strava
        if error or not code:
            if not code:
                msg = "No authorization code recieved from Strava"
            else:
                msg = "Error"
            if error:
                msg = "{}: {}".format(msg, error)
            return self.env.get_template('error.html').render(msg=msg)

        token = Client().exchange_code_for_token(code=code,
                                                 client_id=client_id,
                                                 client_secret=client_secret)
        # Expire current session
        cherrypy.lib.sessions.expire()
        return self.env.get_template('result.html').render(token=token,
                                                           scope=string_for_scope(scope))

def string_for_scope(scope):
    """Return an explanation of the token scope"""
    temp = []
    if "view_private" in scope:
        temp.append("view private activities and data within privacy zones")
    if "write" in scope:
        if temp:
            temp.append(", as well as")
        temp.append("modify activities and upload on your behalf")
    if temp:
        return " ".join(temp)
    return "view public activities (excluding data within privacy zones)"


def create_default_config(sample_conf):
    """Create a default config file template"""
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            f.write(sample_conf)
    except OSError:
        msg = "ERROR: Failed to create the config file template - create it "\
              "manually with the following contents:"
        print(textwrap.fill(msg, width=90, subsequent_indent="       "))
        print("{1}\n{0}\n{1}".format(sample_conf, '-'*60))


def required_config(sample_conf):
    """Use the sample config to get the required configuration options"""
    conf_parser = ConfigParser()
    conf_parser.read_string(sample_conf)
    return {s: tuple(ks.keys()) for s, ks in conf_parser.items() if s != "DEFAULT"}


def validate_config(conf, required):
    """Ensure the config is properly filled out (raises ConfigError if not)"""

    for section, keys in required.items():
        if section not in conf:
            raise ConfigError("A '[{}]' section is required".format(section))
        for key in keys:
            if not conf[section].get(key):
                raise ConfigError("A '{}' value in the '[{}]' section is required"
                                  "".format(key, section))


def run_server():
    """Create a default config file if one doesn't exist and run the server"""
    sample_conf = pkg_resources.resource_string(__name__, "strava-tokengen.conf").decode('utf-8')
    required = required_config(sample_conf)

    config = ConfigParser()
    try:
        with open(CONFIG_FILE, 'r') as f:
            config.read_file(f)
    except FileNotFoundError:
        msg = "WARNING: Creating the config file template at '{}'. You will "\
              "need to modify it before this application will work properly."\
              "".format(CONFIG_FILE)
        print(textwrap.fill(msg, width=90, subsequent_indent="         "))

        create_default_config()
        return

    validate_config(config, required)
    server_conf = config['strava-tokengen']

    cherrypy.config.update({
        'environment': 'production',
        'log.screen': True,
        'server.socket_host': server_conf['host'],
        'server.socket_port': int(server_conf['port'])
    })

    static_dir = pkg_resources.resource_filename(__name__, "static")
    cherry_conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.sessions.timeout': 60
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': static_dir,
            'tools.gzip.on': True,
        }
    }

    app = StravaTokenGen(server_conf['callback_domain'])
    cherrypy.tree.mount(app, '/', config=cherry_conf)
    cherrypy.engine.start()
    cherrypy.engine.block()
