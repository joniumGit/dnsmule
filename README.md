# DNSMule

#### Analyze domains from DNS:

This is the only analysis script at the moment for example usage.

> python scripts/analyze.py -h

```
usage: analyze.py [-h] [--sub-domain-count SDC] --limit LIMIT [--skip-dump] FILE

positional arguments:
  FILE

options:
  -h, --help                        (Help)
  --sub-domain-count SDC, -sdc SDC  (Shows common subdomains greater than this)
  --limit LIMIT, -n LIMIT           (Limit to n first records)
  --skip-dump                       (Skips interactive prompt for dumping records)
  --all                             (Doesn't limit analyzing to subdomains)
```

> python scripts/analyze.py -sdc 10 -n -1 --all --skip-dump umbrella-top-1m.csv rules/rules.yml

#### Rules

Check the rule docs in [rules](rules)

#### server

A very simple server example is in [server,py](server/server.py)

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

