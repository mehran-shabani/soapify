# Soapify

This repository contains the `voice_summarizer` Django project for generating transcripts and summaries of uploaded audio.

## Overview
- **`uploader` app** – Implements the user-facing interface and upload orchestration. It manages form handling, media storage, and coordinates the processing workflow once a file is submitted.
- **`summarizer` app** – Provides the integration with OpenAI services. It performs transcription and summarisation tasks by invoking the configured OpenAI API endpoints.

## Setup
1. **Create and activate a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. **Install runtime dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **(Optional) Install development tooling**:
   ```bash
   pip install -r requirements.dev.txt
   ```
4. **Configure environment variables**:
   - Duplicate `.env.example` to `.env` and populate the required values.
   - At minimum, set `OPENAI_API_KEY` (see [Troubleshooting](#troubleshooting)).
5. **Run database migrations**:
   ```bash
   python manage.py migrate
   ```
6. **Launch the development server**:
   ```bash
   python manage.py runserver
   ```
   The site becomes available at `http://127.0.0.1:8000/`.

## Running tests
Execute the full test suite with:
```bash
pytest
```
Continuous integration executes the same command in an offline mode with mocked OpenAI responses, so CI runs do not consume OpenAI API quota.

## Automation

### Continuous integration (`.github/workflows/ci.yml`)
- Runs on pushes and pull requests that target the `main` branch.
- Exercises the project against Python 3.10 and 3.11, installs runtime and development dependencies, provisions a dummy `.env`, runs database migrations, and executes the pytest suite (uploading the log if tests fail).

### Release (`.github/workflows/release.yml`)
- Triggers whenever a Git tag matching `v*` is pushed.
- Builds an `app-dist.zip` archive without transient media, database, or cache files and publishes it with a GitHub Release.
- Builds and pushes the Docker image `ghcr.io/<owner>/<repo>:<tag>` from the repository `Dockerfile`, authenticating with the provided `GITHUB_TOKEN`.

## Docker image
Pull and run the latest published image from GitHub Container Registry:
```bash
docker pull ghcr.io/<owner>/<repo>:latest
docker run --env-file .env --publish 8000:8000 ghcr.io/<owner>/<repo>:latest
```
Ensure the `.env` file is available locally so the container can access the required OpenAI credentials.

## Troubleshooting
- **Missing API keys** – The application requires `OPENAI_API_KEY` in `.env`. Without it, uploads cannot be processed.
- **Custom OpenAI base URL** – If you use a proxy or Azure OpenAI endpoint, set `OPENAI_BASE_URL` in `.env`. This variable is optional; omit it to use the default OpenAI API host.
- **File size and formats** – Uploads should be common audio/video formats supported by OpenAI Whisper (e.g., MP3, WAV, MP4). Extremely large files may be rejected or take longer to process.
- **Media cleanup** – Temporary media generated during processing is periodically cleaned up. If you need to retain outputs, archive them outside the default media directory.

