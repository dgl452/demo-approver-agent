export const APPROVERS = ["dgl452", "dgliria"];
export const STATUS_CONTEXT = "pr-risk/approval";

export function reviewersToRequest(approvers, author, requestedReviewers) {
  const authorLogin = author.toLowerCase();
  const requested = new Set(requestedReviewers.map((login) => login.toLowerCase()));
  return approvers.filter(
    (login) => login.toLowerCase() !== authorLogin && !requested.has(login.toLowerCase())
  );
}

const SENSITIVE_PATH = /(^|\/)(security|auth|authentication|authorization|crypto|cryptography|permissions?|secrets?|credentials?)([._-]|\/|$)/i;

export function sensitivePathReason(path) {
  const normalized = path.replaceAll("\\", "/").replace(/^\/+/, "");
  if (/^\.github\/workflows\//i.test(normalized)) {
    return "La PR modifica un workflow de GitHub Actions.";
  }
  if (/(^|\/)CODEOWNERS$/i.test(normalized)) {
    return "La PR modifica CODEOWNERS.";
  }
  if (SENSITIVE_PATH.test(normalized)) {
    return "La PR modifica una ruta relacionada con seguridad, autenticación, permisos o credenciales.";
  }
  return null;
}

export function parseCopilotVerdict(output) {
  let text = output.trim();
  const fenced = text.match(/^```(?:json)?\s*([\s\S]*?)\s*```$/i);
  if (fenced) text = fenced[1];

  const verdict = JSON.parse(text);
  if (
    verdict === null ||
    typeof verdict !== "object" ||
    typeof verdict.needs_human !== "boolean" ||
    typeof verdict.reason !== "string" ||
    verdict.reason.trim().length === 0
  ) {
    throw new Error("Copilot returned a verdict that does not match the required JSON schema.");
  }

  return {
    needsHuman: verdict.needs_human,
    reason: verdict.reason.trim().slice(0, 500),
  };
}

export function currentApprovals(reviews, headSha, allowedApprovers, pullRequestAuthor) {
  const allowed = new Set(allowedApprovers.map((login) => login.toLowerCase()));
  const author = pullRequestAuthor.toLowerCase();
  const latestReviewByUser = new Map();

  for (const review of [...reviews].sort((a, b) =>
    (a.submitted_at ?? "").localeCompare(b.submitted_at ?? "")
  )) {
    const login = review.user?.login?.toLowerCase();
    if (!login || !allowed.has(login) || login === author || !review.submitted_at) continue;
    latestReviewByUser.set(login, review);
  }

  return [...latestReviewByUser.values()]
    .filter((review) => review.state === "APPROVED" && review.commit_id === headSha)
    .map((review) => review.user.login);
}

export function escapeCommentText(value) {
  return value
    .replaceAll("@", "&#64;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, 500);
}
