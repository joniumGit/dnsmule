# DNSMule

#### Analyze domains from DNS:

> python analyze.py -h

```
usage: analyze.py [-h] [--sub-domain-count SDC] --limit LIMIT [--skip-dump] FILE

positional arguments:
  FILE

options:
  -h, --help                        (Help)
  --sub-domain-count SDC, -sdc SDC  (Shows common subdomains greater than this)
  --limit LIMIT, -n LIMIT           (Limit to n first records)
  --skip-dump                       (Skips interactive prompt for dumping records)
```

> python analyze.py --sub-domain-count 10 --limit 1000 fi-domains.txt

#### Current POC Status:

- Retrieve Google, Microsoft, Amazon public IP JSON files
- Scan an address for DNS records
- Try to find A records which match known IP ranges

More Resources And Bookmarks:

- https://thyme.apnic.net/
- https://www.arin.net/resources/manage/irr/
- https://www.ripe.net/analyse/internet-measurements/routing-information-service-ris

What Could be done:

- Catalogue and analyze MX records
    - Lots of google and outlooks services
- See how many have DNSSEC
- Elisa, Telia, etc
- Site verification records
- What kinds of records are available

