# delivr
Anycast CDN Orchestration Platform

TODO:
- zone validation
- record type validation
- Add serial field to zone doc

```yaml
# Salt for Argon2 hashing
salt: my-random-salt

# MongoDB connection URI
database: mongodb://localhost:27017

# ASN
asn: 65000

# Routes
routes:
  - 192.0.2.0/24
  - 2001:db8::/48

# Hostname of nameservers
nameservers:
  - ns1.example.com
  - ns2.example.com
```