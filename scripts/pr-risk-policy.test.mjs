import test from "node:test";
import assert from "node:assert/strict";
import {
  currentApprovals,
  escapeCommentText,
  parseCopilotVerdict,
  reviewersToRequest,
  sensitivePathReason,
} from "./pr-risk-policy.mjs";

test("sensitive paths always require human review", () => {
  for (const path of [
    ".github/workflows/build.yml",
    ".github/CODEOWNERS",
    "CODEOWNERS",
    "src/security/token.ts",
    "src/auth.ts",
    "config/permissions.json",
  ]) {
    assert.ok(sensitivePathReason(path), `${path} should be sensitive`);
  }
});

test("ordinary paths are left to Copilot classification", () => {
  assert.equal(sensitivePathReason("docs/usage.md"), null);
  assert.equal(sensitivePathReason("src/dashboard.ts"), null);
});

test("Copilot verdict must be valid JSON with required fields", () => {
  assert.deepEqual(parseCopilotVerdict('{"needs_human":false,"reason":"Cambio pequeño."}'), {
    needsHuman: false,
    reason: "Cambio pequeño.",
  });
  assert.deepEqual(parseCopilotVerdict('```json\n{"needs_human":true,"reason":"Riesgo alto."}\n```'), {
    needsHuman: true,
    reason: "Riesgo alto.",
  });
  assert.throws(() => parseCopilotVerdict("not json"));
  assert.throws(() => parseCopilotVerdict('{"needs_human":"false","reason":"No es booleano"}'));
});

test("only an eligible approval for the current commit satisfies the gate", () => {
  const reviews = [
    {
      user: { login: "dgl452" },
      state: "APPROVED",
      commit_id: "head",
      submitted_at: "2026-01-01T10:00:00Z",
    },
    {
      user: { login: "dgliria" },
      state: "APPROVED",
      commit_id: "old-head",
      submitted_at: "2026-01-01T11:00:00Z",
    },
    {
      user: { login: "dgl452" },
      state: "CHANGES_REQUESTED",
      commit_id: "head",
      submitted_at: "2026-01-01T12:00:00Z",
    },
  ];
  assert.deepEqual(currentApprovals(reviews, "head", ["dgl452", "dgliria"], "author"), []);
  assert.deepEqual(
    currentApprovals(reviews.slice(0, 2), "head", ["dgl452", "dgliria"], "author"),
    ["dgl452"]
  );
  assert.deepEqual(
    currentApprovals(reviews.slice(0, 1), "head", ["dgl452", "dgliria"], "dgl452"),
    []
  );
});

test("comment text cannot trigger mentions or inject markup", () => {
  assert.equal(escapeCommentText("@dgl452 <script>"), "&#64;dgl452 &lt;script&gt;");
});

test("review requests exclude the PR author and reviewers already requested", () => {
  assert.deepEqual(
    reviewersToRequest(["dgl452", "dgliria"], "DGL452", []),
    ["dgliria"]
  );
  assert.deepEqual(
    reviewersToRequest(["dgl452", "dgliria"], "someone-else", ["DGLIRIA"]),
    ["dgl452"]
  );
});
