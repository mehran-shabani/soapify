# Soapify

This repository contains the `voice_summarizer` Django project for generating transcripts and summaries of uploaded audio.

## Automation

### Continuous integration (`.github/workflows/ci.yml`)
- Runs on pushes and pull requests that target the `main` branch.
- Exercises the project against Python 3.10 and 3.11, installs runtime and development dependencies, provisions a dummy `.env`, runs database migrations, and executes the pytest suite (uploading the log if tests fail).

### Release (`.github/workflows/release.yml`)
- Triggers whenever a Git tag matching `v*` is pushed.
- Builds a `app-dist.zip` archive without transient media, database, or cache files and publishes it with a GitHub Release.
- Builds and pushes the Docker image `ghcr.io/<owner>/<repo>:<tag>` from the repository `Dockerfile`, authenticating with the provided `GITHUB_TOKEN`.
