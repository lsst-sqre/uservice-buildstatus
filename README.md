[![Build Status](https://travis-ci.org/lsst-sqre/sqre-apikit.svg?branch=master)](https://travis-ci.org/lsst-sqre/sqre-apikit)

# sqre-uservice-buildstatus

Check status of CI job by name

## Usage

`GET /`

* Return "OK"; used for GKE Ingress healthcheck

`GET /<buildname>`
`GET /buildstatus/<buildname>`

* Return status of build job <buildname>

## Authorization

This microservice expects a GitHub username and token as a Basic
Authentication header in the request.
