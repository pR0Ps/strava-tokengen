strava-tokengen
===============
A simple OAuth token generator for the Strava API (updated for the new refresh token pattern).

Useful for generating tokens for command line applications and other non-web applications.

Screenshot
----------
![Screenshot](/screenshot.jpg)

Setup
-----
- Create an API application in your [API Application settings] on Strava.
- [optional but recommended] Set up a [virtual environment]
- Use `pip` to install the project (`pip install git+https://github.com/pR0Ps/strava-tokengen` works
  or you can clone the project locally and run `pip install <project dir>`).
- Run `strava-tokengen`.
- On first run it will create a default config file and exit.
- Open the config file and change the options as required.
- Run `strava-tokengen` with a completed config and visit the site it serves in a browser.
- Fill in the client id and client secret for your API application.
- Click the "connect with Strava" button to start the authorization flow.
- On Strava, choose your required scopes and authorize the application.
- Use the API refresh token to access the [Strava API] from any other applications.


Licence
-------
[Mozilla Public License, version 2.0]


  [API Application settings]: https://www.strava.com/settings/api
  [Strava API]: https://strava.github.io/api
  [Mozilla Public License, version 2.0]: https://www.mozilla.org/en-US/MPL/2.0
  [virtual environment]: https://docs.python.org/3/library/venv.html
