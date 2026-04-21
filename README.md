# TalentStreamAI

Squad Five capstone for the Andela AI Engineering Bootcamp. The goal is straightforward on paper: help a candidate move from “I found a role” to “I submitted strong materials” without burning an afternoon on manual rewrites. This repository is the **scaffold** only—FastAPI for the API surface, a static-export Next.js client, and a **Terraform root** that is intentionally empty except for provider wiring, variables, outputs, and comments that describe the AWS shape you are heading toward (Aurora Serverless v2 + Data API, Secrets Manager, ECS or Lambda for LangGraph/OpenRouter, API Gateway + Clerk JWT, CloudFront in front of S3). Implementers add resources when they are ready.

Product direction (for context while you build):

- Ingest a resume plus a job posting URL.
- Diff the candidate’s story against the role (ATS-oriented gap analysis).
- Generate refreshed resume copy, a cover letter with narrative structure, and a Gmail-ready draft.

Implementation details for LangGraph, Gmail, and persistence are intentionally left open so feature teams can own them.


## Prerequisites

Pick what matches how you work day to day:

- **Docker Desktop** (or Docker Engine) plus the Compose plugin for the one-command local stack.
- **[uv](https://docs.astral.sh/uv/getting-started/installation/)** for installing and running the Python service (lockfile-backed).
- **Python 3.12** (`backend/.python-version` helps pyenv/asdf) and **Node.js 20+** for host-only development.
- **Terraform 1.6+** and the **AWS CLI v2** when you touch AWS resources.
- An **AWS account** with credentials (`AWS_PROFILE` or standard access keys) when running Terraform or deploy workflows locally.

Secrets stay out of git. Copy `.env.example` at the **repository root** to `.env` and fill in values for your machine. Deployed environments should load the same keys from your secret manager or GitHub Actions secrets/variables.

## First-time local setup (without Docker)

```bash
chmod +x scripts/*.sh   # first clone only
cp .env.example .env    # optional but recommended
./scripts/bootstrap-local.sh
```

Start each service in its own terminal:

```bash
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

```bash
cd frontend
npm run dev
```

Open `http://localhost:3000` for the UI and `http://localhost:8000/docs` for OpenAPI. The home page calls `/api/v1/health` so you can confirm both halves are talking.

### Environment variables (repo root `.env`)

Both FastAPI (`pydantic-settings`) and Next.js (via `dotenv-cli` in `frontend/package.json` scripts) read from the **same** `.env` at the repository root. Keep per-environment values out of source code—set them here locally, or inject them in CI/CD.

| Key | Consumers | Purpose |
| --- | --- | --- |
| `API_HOST` | API | Bind address inside the container or host. |
| `API_PORT` | API | Port for Uvicorn when you run it manually. |
| `CORS_ORIGINS` | API | Comma-separated browser origins allowed to call the API. |
| `NEXT_PUBLIC_API_URL` | UI (build + browser) | Public API base URL the browser calls. Leave empty for production builds that should call same-origin `/api/*` through CloudFront. |
| `DEPLOYMENT_ENVIRONMENT` | API (`/api/v1/health` metadata) | Optional label such as `local`, `dev`, `staging`, or `prod`. |

## Run the full stack in Docker

```bash
chmod +x scripts/*.sh   # first clone only
cp .env.example .env      # compose interpolation + container env (optional)
./scripts/run.sh
```

- API on `http://localhost:8000`
- UI on `http://localhost:3000`
- Compose runs Uvicorn with `--reload` and bind-mounts `./backend/app` read-only for quick API edits.

Stop everything with `./scripts/stop.sh`.

## Terraform (single root under `terraform/`)

`main.tf` holds the `terraform {}` block (including the empty **S3** `backend "s3" {}` stub), a `locals` name helper, and a **numbered checklist** for the architecture you are building toward. There are **no `resource` blocks** in this repository on purpose.

`variables.tf` / `outputs.tf` / `providers.tf` give you tagging defaults and a couple of outputs (`stack_name`, `aws_region`, `next_steps`) so CI and humans can sanity-check wiring before anyone adds modules or resources.

Nothing in the FastAPI or Next.js code hardcodes `dev`/`staging`/`prod`. Terraform’s `environment` variable is validated to those three values for tags and future state keys.

### Remote state

The `terraform {}` block declares an **S3 backend** (empty configuration). Every `terraform init` needs either:

- `terraform/backend.hcl` (copy `terraform/backend.hcl.example`), or
- `TALENTSTREAM_USE_LOCAL_TF_STATE=1` with `./scripts/deploy-aws.sh` for disposable local state (not for teams).

### Plan / destroy helpers

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# set aws_region, project_name, environment (dev | staging | prod)
```

From the repository root:

```bash
./scripts/deploy-aws.sh            # writes a plan (no apply)
./scripts/deploy-aws.sh staging
TF_ENVIRONMENT=prod ./scripts/deploy-aws.sh
```

`./scripts/destroy-aws.sh` is a thin wrapper around `terraform destroy` for when resources eventually exist.

## Project structure

Repository root **`TalentStreamAI/`** 

```text
TalentStreamAI/
├── backend/                         # FastAPI API (uv / pyproject.toml)
│   ├── app/
│   │   ├── main.py                  # App factory + CORS + router mount
│   │   ├── api/                     # HTTP routers (e.g. v1/health)
│   │   ├── core/                    # Settings (reads repo-root .env)
│   │   └── services/
│   │       └── langgraph/           # Placeholder for agent graphs / tools
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── uv.lock
├── frontend/                        # Next.js 15 (App Router, static export)
│   ├── src/
│   │   ├── app/                     # Routes, layouts, pages
│   │   └── lib/                     # Shared helpers (e.g. API URL builder)
│   ├── public/                      # Static assets for export
│   ├── Dockerfile                   # Multi-stage: Node build → nginx serves out/
│   ├── next.config.ts
│   └── package.json
├── terraform/                       # AWS scaffold (no resources yet)
│   ├── main.tf                      # terraform {} + locals + architecture checklist
│   ├── variables.tf
│   ├── outputs.tf
│   ├── providers.tf
│   ├── backend.hcl.example
│   ├── terraform.tfvars.example
│   └── .terraform.lock.hcl
├── scripts/
│   ├── bootstrap-local.sh           # uv sync + npm install
│   ├── run.sh / stop.sh             # Docker Compose up / down
│   └── deploy-aws.sh / destroy-aws.sh   # Terraform plan / destroy helpers
├── .github/
│   ├── workflows/                   # CI + deploy placeholder workflows
│   └── aws/
│       └── github-oidc-trust-policy.json.example
├── docker-compose.yml               # Local API (:8000) + static UI (:3000 → nginx :80)
├── .env.example                     # Shared env template (copy to repo-root .env)
├── .gitignore
└── README.md
```

## GitHub Actions (scaffold)

`.github/workflows/ci.yml` runs on pushes and pull requests to `main` but **only checks out the repository** and echoes that real CI is still to be defined (backend uv/tests, frontend npm/lint/build, Terraform fmt/validate, and so on).

`.github/workflows/deploy-aws.yml` is **manual (`workflow_dispatch`) only** and does **not** call AWS or Terraform. It prints a short checklist for when you add OIDC, secrets, `terraform apply`, image pushes, and static asset publishing.

For OIDC trust policy shaping, see `.github/aws/github-oidc-trust-policy.json.example` and replace `ACCOUNT_ID`, `GITHUB_ORG`, and `REPO` before attaching it to an IAM role.

## Where feature work should land

- **FastAPI routers**: add packages under `backend/app/api/v1/` (or new version folders) and include them from `backend/app/api/router.py`.
- **Agents / LangGraph**: keep graphs, tools, and state machines under `backend/app/services/langgraph/` so onboarding stays predictable.
- **UI routes and data fetching**: colocate routes in `frontend/src/app` (static export friendly) and keep shared helpers in `frontend/src/lib`.
- **Infrastructure growth**: add child modules under `terraform/modules/` (or keep everything flat) and call them from `terraform/main.tf` once you outgrow the four-file scaffold.

## Quality gates (lightweight for now)

```bash
cd frontend && npm run lint && npm run build
```

```bash
cd backend && uv sync && uv run python -m compileall -q app
```

Add pytest, Ruff, or mypy when the API surface grows; the scaffold stays intentionally small.

## Troubleshooting quick hits

- **UI shows “Backend not responding.”** Confirm Uvicorn is listening on `8000`, `CORS_ORIGINS` includes your UI origin, and `NEXT_PUBLIC_API_URL` matches how your browser reaches the API.
- **`docker compose` cannot reach Docker.** Start Docker Desktop (macOS/Windows) or the Linux daemon, then rerun `./scripts/run.sh`.
- **Terraform init asks for backend settings.** Create `terraform/backend.hcl` or export `TALENTSTREAM_USE_LOCAL_TF_STATE=1` for disposable local state.
- **GitHub Actions.** The bundled workflows are placeholders only; there is nothing to “fix” for credentials until you replace them with real jobs.


