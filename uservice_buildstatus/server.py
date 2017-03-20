#!/usr/bin/env python
"""Retrieve build data from ci.lsst.codes"""
import requests
from apikit import APIFlask as APF
from apikit import BackendError
from flask import jsonify, request

# pylint: disable=invalid-name
log = None


def server(run_standalone=False):
    """Create the app and then run it."""
    # Add "/buildstatus" for mapping behind api.lsst.codes
    # Also "/bldstatus"
    app = APF(name="uservice-buildstatus",
              version="0.0.3",
              repository="https://github.com/sqre-lsst/" +
              "sqre-uservice-buildstatus",
              description="API wrapper for build status",
              route=["/", "/buildstatus", "/bldstatus"],
              auth={"type": "basic",
                    "data": {"username": "",
                             "password": ""}})
    app.config["SESSION"] = None
    # pylint: disable=global-statement
    global log
    log = app.config["LOGGER"]

    @app.route("/")
    # pylint: disable=unused-variable
    def return_root():
        '''For GKE Ingress healthcheck'''
        return "OK"

    @app.route("/<buildname>")
    @app.route("/buildstatus/<buildname>")
    @app.route("/bldstatus/<buildname>")
    # pylint: disable=unused-variable
    def get_buildstatus(buildname):
        """
        Proxy for ci.lsst.codes.  We expect the incoming request to have
        Basic Authentication headers.
        """
        inboundauth = None
        if request.authorization is not None:
            inboundauth = request.authorization
            currentuser = app.config["AUTH"]["data"]["username"]
            currentpw = app.config["AUTH"]["data"]["password"]
            if currentuser != inboundauth.username or \
               currentpw != inboundauth.password:
                _reauth(app, inboundauth.username, inboundauth.password)
        else:
            raise BackendError(reason="Unauthorized", status_code=403,
                               content="No authorization provided.")
        session = app.config["SESSION"]
        url = "https://ci.lsst.codes/job/" + buildname + "/api/json"
        log.info("Requesting URL %s" % url)
        resp = session.get(url)
        if resp.status_code == 403:
            # Try to reauth
            log.warning("Authorization failed; attempting reauth.")
            _reauth(app, inboundauth.username, inboundauth.password)
            session = app.config["SESSION"]
            log.info("Requesting URL %s" % url)
            resp = session.get(url)
        if resp.status_code == 200:
            return resp.text
        else:
            raise BackendError(reason=resp.reason,
                               status_code=resp.status_code,
                               content=resp.text)

    @app.route("/")
    # pylint: disable=unused-variable
    def root_route():
        """Needed for Ingress health check."""
        return "OK"

    @app.errorhandler(BackendError)
    # pylint: disable=unused-variable
    def handle_invalid_usage(error):
        """Custom error handler."""
        errdict = error.to_dict()
        response = jsonify(errdict)
        log.error(errdict)
        response.status_code = error.status_code
        return response
    if run_standalone:
        app.run(host='0.0.0.0', threaded=True)
    # Cough up app for uwsgi
    return app


def _reauth(app, username, password):
    """Get a session with authentication data"""
    session = requests.Session()
    session.auth = (username, password)
    # pylint: disable=global-statement
    global log
    log = log.bind(username=username)
    log.info("Established session with username %s" % username)
    app.config["SESSION"] = session


def standalone():
    """Entry point for running as its own executable."""
    server(run_standalone=True)


if __name__ == "__main__":
    standalone()
