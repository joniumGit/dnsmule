# DNSMule Server

A very simple server example is in [server,py](server.py)

Requires:

- `fastapi`
- `uvicorn`

> pip install fastapi uvicorn

The server allows adding, viewing, and deleting rules.
It is possible to run scans for domains and rescan all domains with results.
There is no data persistence except for memory at the moment.

__Security Note:__ The server allows adding dynamic rules, so don't run it public.

Example commands:

```shell
$ curl -X DELETE http://localhost:8000/rules\?record=txt\&name=ses
$ curl -s http://localhost:8000/rules | python -m json.tool
$ curl -X POST http://localhost:8000/scan\?domain=ouspg.org
$ curl -s http://localhost:8000/results\?domain=ouspg.org | python -m json.tool
```

You can interface with the server through the Swagger doc:

> http://localhost:8000/docs
