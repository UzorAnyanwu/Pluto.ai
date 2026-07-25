# infra/docker

`docker-compose.yml` for local development: Postgres+pgvector, Redis, and localstack (S3/SNS/SQS
emulation). See [`docs/architecture/05-infra-and-observability.md`](../../docs/architecture/05-infra-and-observability.md) §6.

```bash
docker compose -f infra/docker/docker-compose.yml up -d
```

`services/api-core/Dockerfile` is the only per-service Dockerfile that exists so far (built from
the repo root — see the comment at the top of that file for why). Additional services get their
own Dockerfile as they're built; there is no shared base image yet since there's only one Python
service to share anything with.

**Not exercised in this repo's own development** — this machine had no Docker available, so the
Postgres/Redis setup used to build and test `libs/pluto_core`/`services/api-core` was a native
Homebrew install instead (see `scripts/bootstrap_local_db.sh`). This compose file is written to
the same architecture (pgvector-enabled Postgres image, matching role bootstrap in
`init-db.sh`) but hasn't been run end-to-end — validate it the first time a machine with Docker
picks this repo up.
