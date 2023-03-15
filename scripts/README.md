# Miscellaneous Scripts

These are subject to removal at any point.

#### Analyze most common subdomains

Analyzes a list of domains for most common subdomain entries.

```text
usage: dstat.py [-h] [-n N] FILE

Lists top domains and top first subdomains

positional arguments:
  FILE             input domain file (txt or csv[id, value])

options:
  -h, --help       show this help message and exit
  -n N, --limit N  limit the outputs to top-n entries
```

```text
python dstat.py -n 10 umbrella-top-1m.csv

Total entries: 1000000

Top domains
0        24281 googlevideo.com
1        15259 amazonaws.com
2        14700 fbcdn.net
3        14088 co.uk
4        13466 sharepoint.com
5         9782 webex.com
6         8018 edgekey.net
7         6290 windows.net
8         6184 gvt1.com
9         5544 akamaiedge.net

Top sub-domains
0        68308 www
1        16176 cdn
2        15832 fna
3        14200 com
4        13333 api
5         6049 c
6         5867 infra
7         5491 elb
8         4621 app
9         4595 fls
```

#### Post data to server from file

Requires `httpx` library.

```
usage: post_to_server.py [-h] [--host HOST] [--port PORT] [--https] [--skip SKIP] [--delay DELAY] [--suffix SUFFIX] file

positional arguments:
  file             input domain file (txt or csv[id, value])

options:
  -h, --help       show this help message and exit
  --host HOST      server host
  --port PORT      server port
  --https          use https
  --skip SKIP      skip n records
  --delay DELAY    send delay in ms
  --suffix SUFFIX  suffix to filter domains by
```

#### Create Resource Record types

The script `create_rr_types.py` creates the `rrtype.py` file in DNSMule.

#### De-duplicate data in redis

The script `deduplicate_redis.py` connects to a local redis and fixes duplicates from `certcheck` and `ptrscan`.

#### Install Certificates

Copied from standard python install on macOS.

#### Debug IPRanges

Prints all ipranges used by the `ipranges` plugin.

#### Fetch cert

Fetches certificate from domain in both encoded and python tuples modes