# PR risk approver

This repository demonstrates risk-based human approval routing for pull requests. GitHub Copilot already performs the code review; this workflow does not repeat that review. It uses GitHub Copilot CLI with a dedicated custom agent to assess the change's risk and decide whether a human approval is needed.

## Behavior

- Pull request patches and metadata are sent to Copilot CLI for risk/complexity classification only. The agent cannot use tools, make changes, or post review findings.
- Changes to `.github/workflows/**`, `CODEOWNERS`, or paths containing security/authentication/permissions/secret-related segments always require human approval.
- If GitHub omits a patch, the diff is too large for the configured 50,000-character limit, Copilot CLI is unavailable, or its response is invalid, the workflow fails closed and requests human review.
- For changes classified as requiring a human, the workflow requests review from `dgl452` and `dgliria` (excluding the PR author) and requires one of them to approve the current head commit.
- For low-risk changes, the workflow leaves a PR comment and passes its status without requesting human approval.
- The workflow never approves or merges a pull request.

## Required repository setup

1. Add an Actions repository secret named `COPILOT_GITHUB_TOKEN` with a fine-grained PAT that has the **Copilot Requests** permission. The token is used only by Copilot CLI. Enable the CLI policy for the organization/account if required by GitHub.
2. Ensure each configured approver is a repository collaborator with at least read access and can review pull requests. The PR author is excluded from their own approval requirement. For example, on a PR authored by `dgl452`, `dgliria` must be a collaborator; otherwise GitHub rejects the review request and the required status remains blocked.
3. In the default branch's ruleset/branch protection, require the commit status context **`pr-risk/approval`**. Do not require a fixed number of pull request approvals globally if low-risk PRs should merge without one; this workflow enforces one eligible approval only when needed.
4. Require the repository's other CI checks as appropriate. Do not grant a bypass that defeats the required status check.

The workflow uses `pull_request_target` so it can update status, comments, and reviewer requests for fork PRs. It checks out only the trusted default branch and never checks out or executes code from the PR. Keep the workflow, classifier, and custom agent protected by review.

If Copilot CLI reports an authentication error, verify that `COPILOT_GITHUB_TOKEN` is a valid, unexpired token with **Copilot Requests** permission and that its owner has access to Copilot. The workflow passes this credential to Copilot CLI separately from the Actions `GITHUB_TOKEN`; it never prints the secret.

## Local tests

Run the policy unit tests with:

```sh
node --test scripts/pr-risk-policy.test.mjs
```

## Local FastAPI demo

The local-only demo API lives in `services/fastapi-api`. It provides
`GET /api/health` and in-memory CRUD routes under `/api/items`; item data is
cleared when the process stops. It has no datastore, authentication, Azure
services, or deployment configuration.

Install the API and test dependencies from the repository root, then run the
test suite:

```sh
python3 -m pip install -r requirements.txt
python3 -m pytest
```

Start the API locally:

```sh
python3 -m uvicorn app.main:app --app-dir services/fastapi-api --host 127.0.0.1 --port 8000
```

The interactive API docs are available at `http://127.0.0.1:8000/docs`.
