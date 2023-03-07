# Miscellaneous Scripts

These will all be removed most likely.

#### Analyze FI domains from a file and DNS:

Analyzes a list of domains for `*.fi` domains and fetches data about them from DNS.

> python analyze.py -h

```text
usage: analyze.py [-h] [--sub-domain-count SDC] --limit LIMIT [--skip-dump] FILE RULES

positional arguments:
  FILE RULES

options:
  -h, --help                        (Help)
  --sub-domain-count SDC, -sdc SDC  (Shows common subdomains greater than this)
  --limit LIMIT, -n LIMIT           (Limit to n first records)
  --skip-dump                       (Skips interactive prompt for dumping records)
  --all                             (Doesn't limit analyzing to subdomains)
```

> python analyze.py -sdc 10 -n -1 --all --skip-dump umbrella-top-1m.csv rules/rules.yml

#### Analyze most common subdomains

Analyzes a list of domains for most common subdomain entries.

> python dstat.py -h

```text
usage: dstat.py [-h] [-n N] FILE

Lists top domains and top first subdomains

positional arguments:
  FILE             Input file

options:
  -h, --help       show this help message and exit
  -n N, --limit N  Limit to top n-entries
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

#### Create Resource Record types

The script `create_rr_types.py` creates the `rrtype.py` file in DNSMule.