# delivr
Anycast CDN Orchestration Platform

### Configuration
delivr is configured with the `config.yml` file located in the root directory. Make sure to adjust the values to suit your deployment.

```yaml
# Salt for Argon2 hashing
salt: random-salt

# MongoDB connection URI
database: mongodb://localhost:27017

# Server
server-host: localhost
server-port: 3000

# Enable verbose Flask error messages and static secret key. WARNING: Don't enable this in production!
development: false

nameservers:
  - ns1.example.com
  - ns2.example.com

soa-root: root.delivr.dev
```