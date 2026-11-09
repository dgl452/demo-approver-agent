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
2. Ensure `dgl452` and `dgliria` are collaborators who can review pull requests.
3. In the default branch's ruleset/branch protection, require the commit status context **`pr-risk/approval`**. Do not require a fixed number of pull request approvals globally if low-risk PRs should merge without one; this workflow enforces one eligible approval only when needed.
4. Require the repository's other CI checks as appropriate. Do not grant a bypass that defeats the required status check.

The workflow uses `pull_request_target` so it can update status, comments, and reviewer requests for fork PRs. It checks out only the trusted default branch and never checks out or executes code from the PR. Keep the workflow, classifier, and custom agent protected by review.

## Local tests

Run the policy unit tests with:

```sh
node --test scripts/pr-risk-policy.test.mjs
```
