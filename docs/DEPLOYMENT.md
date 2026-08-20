# Deploy Ticketifier to Ubuntu 24.04

## 1. DNS

In your DNS provider, create an `A` record for `YOUR_APP_DOMAIN` pointing to `YOUR_VPS_IPV4`, with TTL `300` or the default. Add `AAAA` only when the VPS has working public IPv6. Do not commit the real VPS address to this repository.

## 2. Read-only VPS inventory

```bash
lsb_release -ds
docker version --format '{{.Server.Version}}'
docker compose version
sudo nginx -T 2>/dev/null | awk '$1 == "server_name" {for (i=2; i<=NF; i++) print $i}' | tr -d ';' | sort -u
sudo ss -lntp
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Ports}}'
docker compose ls
df -h
free -h
sudo ufw status
systemctl is-active nginx docker
certbot --version
id
```

Redact the deployment username before sharing output. Choose and verify `YOUR_UNUSED_LOOPBACK_PORT`; do not reuse another service's port.

## 3. Application directory and environment

```bash
sudo install -d -m 750 -o YOUR_DEPLOY_USER -g YOUR_DEPLOY_GROUP /opt/ticketifier
install -d -m 750 /opt/ticketifier/deploy
```

Create `/opt/ticketifier/.env` with mode `0600`:

```dotenv
ENVIRONMENT=production
APP_URL=https://YOUR_APP_DOMAIN
TICKETIFIER_PORT=YOUR_UNUSED_LOOPBACK_PORT
TRUSTED_ORIGINS=https://YOUR_APP_DOMAIN
DEFAULT_OPENAI_MODEL=gpt-5-mini
ALLOWED_OPENAI_MODELS=gpt-5-mini,gpt-5.2
REQUEST_TIMEOUT_SECONDS=60
MAX_OUTPUT_TOKENS=1200
REQUESTS_PER_HOUR=30
API_DOCS_ENABLED=false
```

There is no application OpenAI key or other production credential in `.env`. Each visitor supplies a key for one request.

## 4. GHCR and GitHub Actions

For private images, log the VPS into GHCR interactively using a token limited to `read:packages`. Create a dedicated SSH deployment key and a protected GitHub environment named `production` with:

- `VPS_HOST`
- `VPS_SSH_PORT`
- `VPS_USER`
- `VPS_SSH_PRIVATE_KEY`
- `VPS_KNOWN_HOSTS`

Verify the SSH host-key fingerprint through an already trusted connection before storing `VPS_KNOWN_HOSTS`. Push to `main`; CI tests, audits, builds immutable SHA-tagged images, deploys only the `ticketifier` project, checks readiness, and restores previous image tags on failure.

## 5. Nginx and TLS

Copy `deploy/nginx/ticketifier.conf.example` to `/etc/nginx/sites-available/YOUR_APP_DOMAIN`, replace its domain/loopback-port placeholders, then:

```bash
sudo ln -s /etc/nginx/sites-available/YOUR_APP_DOMAIN /etc/nginx/sites-enabled/YOUR_APP_DOMAIN
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d YOUR_APP_DOMAIN
sudo certbot renew --dry-run
```

Never reload Nginx when `nginx -t` fails. Do not modify another virtual host.

## 6. Smoke test

```bash
curl --fail --silent --show-error https://YOUR_APP_DOMAIN/api/health/ready
```

Open the site, submit a low-cost test with your own key, confirm the output and four REST transcript hops, confirm the displayed authorization value is `[REDACTED]`, and ensure the API-key field clears after submission.

Authoritative references: [Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/), [Certbot with Nginx](https://certbot.eff.org/instructions?ws=nginx&os=snap), and [OpenAI model/Responses guidance](https://developers.openai.com/api/docs/guides/latest-model).
