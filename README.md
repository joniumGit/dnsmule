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

