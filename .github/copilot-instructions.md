# Copilot / AI Agent Instructions — weather-robot

Purpose: Help AI coding agents become productive quickly in this repository by documenting the project's structure, discovered conventions, integration points, and safe next steps.

**Quick Context**:
- **Repo root**: minimal `README.md` only.
- **Function code**: `function/FetchWeather/` (currently empty) — this is the expected location for the serverless function that fetches weather data.
- **Infrastructure**: `infra/` (contains infrastructure-as-code or deployment configs).
- **CI workflows**: `.github/workflows/` exists but contains no workflows in this snapshot.

**Big Picture / Architecture (discoverable)**
- Single-purpose project that separates deployment/infrastructure from runtime code:
  - `function/FetchWeather/` — serverless function implementation (one function per folder convention).
  - `infra/` — infrastructure or deployment definitions (cloud-specific files may live here).
- Integration pattern: function code is expected to be deployed by infra; function likely reaches external weather APIs and/or a scheduler. No evidence of a database or message bus in the current tree.

**What to inspect first (key files/dirs)**
- `function/FetchWeather/` — function source, tests, and package manifest (e.g., `package.json`, `requirements.txt`, or equivalent runtime files) will be placed here.
- `infra/` — check for Terraform, Bicep, ARM, CloudFormation, or IaC configs; this directory defines deployment shape and environment variables/secrets.
- `.github/workflows/` — CI workflows; if absent, do not assume tests run automatically.
- `README.md` — lightweight project description; may contain additional notes from maintainers.

**Project-specific conventions (observed)**
- Single responsibility per folder: each function/service gets its own folder under `function/`.
- Keep infra and runtime code separated: infrastructure changes belong in `infra/` and runtime code in `function/`.
- No test harness or build scripts are present in the repo snapshot. Do not infer test commands — ask the owner before running or adding automation.

**Developer workflows & checks (what is discoverable / safe defaults)**
- There are no build/test scripts checked in. Before running anything, ask the user for the runtime (Node, Python, etc.) and preferred cloud provider.
- Safe investigation steps an agent can perform without external credentials:
  - Open `function/FetchWeather/` to look for entrypoint filenames (e.g., `index.js`, `handler.py`).
  - Open `infra/` to identify IaC type (Terraform `.tf`, ARM/Bicep, CloudFormation `.yml`).
  - Report missing or ambiguous runtime metadata and request clarification.

**Integration points & external dependencies (based on repo layout)**
- Expect external weather API(s) called from the function; credentials (API keys) are likely required and should be stored in secrets — do not add keys to the repo.
- Deployment is driven by files in `infra/` or by CI workflows (none currently present). Confirm which cloud provider (Azure, AWS, GCP) and which deployment mechanism the maintainer intends.

**Examples & patterns (copy/pasteable hints for agents)**
- To locate the function entrypoint, look for these filenames in `function/FetchWeather/`:
  - Node: `index.js`, `app.js`, `package.json` (look for a `main` or `scripts` entry)
  - Python: `__init__.py`, `handler.py`, `requirements.txt`
- To identify infra type, search `infra/` for file extensions: `.tf`, `.bicep`, `.json` (ARM), `.yml` (CloudFormation/SAM)

**When updating or adding files**
- Keep changes minimal and focused. If adding runtime code, place it under `function/FetchWeather/` and update `infra/` only if required for deployment.
- If creating CI workflows, put them in `.github/workflows/` and explicitly document their purpose in the workflow file.

**Merging with existing agent docs (if present)**
- If a `.github/copilot-instructions.md` already exists in future, preserve any repository-specific tooling commands or secrets-handling notes. Merge new high-level architecture and examples into the existing file rather than replacing it wholesale.

**Open questions for the maintainer (ask before proceeding with non-trivial changes)**
- Which cloud provider and runtime are intended for `FetchWeather`?
- Are there any local or CI commands you use to build, test, or run the function locally (e.g., Azure Functions Core Tools, `sam local`, `func start`, `npm run start`)?
- Where are secrets stored for deployments (Azure Key Vault, AWS Secrets Manager, GitHub Actions secrets)?

If anything in this file is unclear or you want agent guidance to be extended (for example adding example CI workflows or a local run script), tell me which cloud/runtime and I will update this document accordingly.

**Concrete Example: Python runtime + Azure Functions**

- Recommended function layout for a simple HTTP-triggered Python function:
  - `function/FetchWeather/function_app/__init__.py` -- contains the function handler (or use the Azure Functions function structure with a folder per function)
  - `function/FetchWeather/requirements.txt` -- Python dependencies
  - `function/FetchWeather/host.json` and `function/FetchWeather/local.settings.json` (local settings; do NOT check secrets into repo)

- Minimal `requirements.txt` example:
  - `azure-functions==1.10.0`
  - `requests`

- Local run/debug tips:
  - Install Azure Functions Core Tools and Python v3.8+ (match your target runtime). Run: `func start` inside the function folder.
  - Use `local.settings.json` for local secrets; never commit this file. Add required secrets to GitHub Actions or Azure Key Vault for deployments.

- Secrets and deployment:
  - For GitHub Actions deploys we recommend storing the function publish profile in the secret `AZURE_FUNCTIONAPP_PUBLISH_PROFILE` (or use `AZURE_CREDENTIALS` for service principal deployment).

**Example GitHub Actions workflow (deploy to Azure Functions)**

Below is a minimal CI workflow you can place in `.github/workflows/deploy-azure-function.yml`. It installs Python, installs dependencies, runs any tests, and deploys the function using the publish profile stored in the repository secret `AZURE_FUNCTIONAPP_PUBLISH_PROFILE`.

```yaml
name: Deploy Azure Function (Python)

on:
  push:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        working-directory: ./function/FetchWeather
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests
        working-directory: ./function/FetchWeather
        run: |
          # add your test command here (example using pytest)
          if [ -f pytest.ini ]; then pytest -q; fi

      - name: Deploy to Azure Functions
        uses: azure/functions-action@v1
        with:
          app-name: ${{ secrets.AZURE_FUNCTIONAPP_NAME }} # set this secret in repo settings
          package: './function/FetchWeather'
          publish-profile: ${{ secrets.AZURE_FUNCTIONAPP_PUBLISH_PROFILE }}

```

Notes:
- Replace `secrets.AZURE_FUNCTIONAPP_NAME` and `secrets.AZURE_FUNCTIONAPP_PUBLISH_PROFILE` with repository secrets. The publish profile is obtained from the Azure portal (Function App -> Get publish profile).
- If you prefer to use a service principal, create `AZURE_CREDENTIALS` and use the `azure/login` action to authenticate prior to deployment.

If you want, I can add the example workflow file to the repo and create a small Python function skeleton under `function/FetchWeather/` so the workflow can be exercised locally. Tell me which Python minor version to target (e.g., `3.10`), and whether to scaffold an HTTP-triggered function or a timer-triggered one.
