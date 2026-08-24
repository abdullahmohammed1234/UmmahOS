const listeners = new Set();

export const state = {
  screen: "landing",
  topics: [],
  subjects: [],
  subject: null,
  session: null,
  result: null,
  trace: null,
  summary: null,
  story: null,
  progress: null,
  insights: null,
  journey: null,
  journeyStep: null,
  counterfactual: null,
  content: null,
  researchOpen: false,
  researchPage: false,
  noticedOpen: true,
  whyOpen: true,
  detailOpen: false,
  navOpen: false,
  submitting: false,
  loading: false,
  error: null,
  demo: null,
  learnerId: null,
};

export function setState(patch) {
  Object.assign(state, patch);
  listeners.forEach((fn) => fn(state));
}

export function subscribe(fn) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

export function errorMessage(error) {
  const code = error && error.code;
  if (code === "session_unavailable") return "This session is no longer available. Start a new one to continue.";
  if (code === "invalid_response") return "Please enter an answer and choose how confident you are.";
  if (code === "challenge_unavailable") return "A challenge isn’t available right now. Try another topic.";
  if (code === "session_complete") return "This session is complete.";
  if (code === "submission_error") return "ADAPT couldn’t process that just now. Please try again.";
  return (error && error.message) || "Something went wrong. Please try again.";
}
