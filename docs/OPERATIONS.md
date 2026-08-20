# Operations

Run Compose commands from `/opt/ticketifier`:

```bash
docker compose --project-name ticketifier --env-file .env --env-file image.env -f compose.production.yml COMMAND
```

## Health, logs, and resources

```bash
curl --fail --silent --show-error https://YOUR_APP_DOMAIN/api/health/live
curl --fail --silent --show-error https://YOUR_APP_DOMAIN/api/health/ready
docker compose --project-name ticketifier --env-file .env --env-file image.env -f compose.production.yml ps
docker compose --project-name ticketifier --env-file .env --env-file image.env -f compose.production.yml logs --since 30m api gateway
docker stats --no-stream
df -h
free -h
```

Restart only Ticketifier:

```bash
docker compose --project-name ticketifier --env-file .env --env-file image.env -f compose.production.yml restart
```

## Data, rollback, and manual deployment

Ticketifier stores no application data, API keys, accounts, or request history, so there is no application database to back up or restore. Back up only the VPS configuration through your existing protected system.

Failed automated releases restore the previous `image.env`. To deploy a previously published tested SHA manually:

```bash
/opt/ticketifier/deploy/deploy-release.sh YOUR_GITHUB_OWNER/YOUR_REPOSITORY YOUR_FULL_TESTED_COMMIT_SHA /opt/ticketifier
```

## Troubleshooting

- `401`: OpenAI rejected the supplied key.
- `403`: the key cannot access the selected model.
- `429`: Ticketifier's hourly limit or the key's OpenAI quota/rate limit was reached.
- `504`: OpenAI exceeded the bounded timeout.
- Gateway unhealthy: inspect only recent `gateway` and `api` logs and check the loopback readiness endpoint.
- Never paste keys, request bodies containing keys, `.env`, or unrelated Nginx configuration into tickets or chat.
