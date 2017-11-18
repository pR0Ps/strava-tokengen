strava-tokengen
===============
A simple OAuth token generator for the Strava API.

Useful for generating tokens for command line applications and other non-web applications.

Screenshot
----------
![Screenshot](/screenshot.jpg)

Setup
-----
- Create an API application in your [API Application settings] on Strava.
- `pip install strava-tokengen` and run `strava-tokengen`.
- On first run it will create a default config file and exit.
- Open the config file and change the options as required.
- Run `strava-tokengen` with a completed config and visit the site it serves in a browser.
- Fill in the client id and client secret for your API application and choose the permissions the
  generated token will have.
- Click the "connect with Strava" button to generate an API token.
- Use the API token to access the [Strava API] from any other applications.


Licence
-------
[Mozilla Public License, version 2.0]


  [API Application settings]: https://www.strava.com/settings/api
  [Strava API]: https://strava.github.io/api
  [Mozilla Public License, version 2.0]: https://www.mozilla.org/en-US/MPL/2.0
