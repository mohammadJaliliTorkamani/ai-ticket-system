#!/usr/bin/env bash
set -Eeuo pipefail

if [[ $# -ne 3 ]]; then
  echo "Usage: deploy-release.sh IMAGE_NAMESPACE RELEASE_SHA DEPLOY_DIR" >&2
  exit 64
fi

image_namespace="${1,,}"
release_sha="$2"
deploy_dir="$3"

if [[ ! "$release_sha" =~ ^[0-9a-f]{40}$ ]]; then
  echo "Release SHA must be a full Git commit SHA." >&2
  exit 64
fi
if [[ "$deploy_dir" != "/opt/ticketifier" ]]; then
  echo "Refusing to deploy outside /opt/ticketifier." >&2
  exit 64
fi

cd "$deploy_dir"
test -f .env
test -f compose.production.yml

previous_image_env=""
if [[ -f image.env ]]; then
  previous_image_env="$(mktemp "$deploy_dir/.image.env.previous.XXXXXX")"
  cp image.env "$previous_image_env"
  chmod 600 "$previous_image_env"
fi

umask 077
{
  printf 'API_IMAGE=ghcr.io/%s/api:%s\n' "$image_namespace" "$release_sha"
  printf 'WEB_IMAGE=ghcr.io/%s/web:%s\n' "$image_namespace" "$release_sha"
} > image.env

compose=(docker compose --project-name ticketifier --env-file .env --env-file image.env -f compose.production.yml)

rollback() {
  echo "Deployment health check failed; restoring the previous release." >&2
  if [[ -n "$previous_image_env" && -f "$previous_image_env" ]]; then
    cp "$previous_image_env" image.env
    "${compose[@]}" pull --quiet
    "${compose[@]}" up -d --remove-orphans
    rm -f -- "$previous_image_env"
  else
    "${compose[@]}" stop gateway api || true
  fi
}
trap rollback ERR

"${compose[@]}" pull --quiet
"${compose[@]}" up -d --remove-orphans

healthy=false
for _attempt in $(seq 1 30); do
  if "${compose[@]}" exec -T gateway wget -q -O /dev/null http://127.0.0.1:8080/api/health/ready; then
    healthy=true
    break
  fi
  sleep 2
done
test "$healthy" = true

trap - ERR
if [[ -n "$previous_image_env" ]]; then
  rm -f -- "$previous_image_env"
fi
"${compose[@]}" ps
echo "Ticketifier release ${release_sha:0:12} is healthy."
