strava-tokengen
===============
A simple OAuth token generator for the Strava API.

Useful for generating tokens for command line applications and other non-web applications.

Setup
-----
- Create an API application in your [API Application settings] on Strava.
- `pip install strava-tokengen` and run `strava-tokengen`.
- On first run it will create a default config file and exit.
- Edit the config file and add in your `client_id`, `client_secret` and `redirect_uri` under the
  `strava` section.
- The server configuration is also stored in this file. The application uses [CherryPy] as a web
  framework so all the regular configuration options are available. See the [CherryPy documentation] for more details.
- Run `strava-tokengen` with a completed config and visit the site in a browser to generate an API token.
- Use the API token to access the [Strava API] from whatever application you want.


Licence
-------
[Mozilla Public License, version 2.0]


  [API Application settings]: https://www.strava.com/settings/api
  [Strava API]: https://strava.github.io/api
  [CherryPy]: http://cherrypy.org/
  [CherryPy documentation]: http://docs.cherrypy.org/en/latest/config.html
  [Mozilla Public License, version 2.0]: https://www.mozilla.org/en-US/MPL/2.0
