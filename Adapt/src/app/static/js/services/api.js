const headers = { "Content-Type": "application/json" };

async function request(path, options = {}) {
  const response = await fetch(path, options);
  let data = {};
  try {
    data = await response.json();
  } catch {
    data = { error: "submission_error", message: "The server returned an unreadable response." };
  }
  if (!response.ok) {
    const error = new Error(data.message || "Request failed");
    error.code = data.error || "submission_error";
    error.status = response.status;
    throw error;
  }
  return data;
}

export const api = {
  topics() {
    return request("/api/topics");
  },
  subjects(learnerId) {
    const q = learnerId ? `?learner_id=${encodeURIComponent(learnerId)}` : "";
    return request(`/api/subjects${q}`);
  },
  subject(id, learnerId) {
    const q = learnerId ? `?learner_id=${encodeURIComponent(learnerId)}` : "";
    return request(`/api/subjects/${encodeURIComponent(id)}${q}`);
  },
  createSession(payload) {
    return request("/api/sessions", { method: "POST", headers, body: JSON.stringify(payload) });
  },
  getSession(id) {
    return request(`/api/sessions/${encodeURIComponent(id)}`);
  },
  submitResponse(id, payload) {
    return request(`/api/sessions/${encodeURIComponent(id)}/responses`, {
      method: "POST",
      headers,
      body: JSON.stringify(payload),
    });
  },
  trace(id) {
    return request(`/api/sessions/${encodeURIComponent(id)}/trace`);
  },
  summary(id) {
    return request(`/api/sessions/${encodeURIComponent(id)}/summary`);
  },
  story(id) {
    return request(`/api/sessions/${encodeURIComponent(id)}/story`);
  },
  progress(id) {
    return request(`/api/sessions/${encodeURIComponent(id)}/progress`);
  },
  progressQuery(learnerId) {
    const q = learnerId ? `?learner_id=${encodeURIComponent(learnerId)}` : "";
    return request(`/api/progress${q}`);
  },
  journeyQuery(learnerId, subjectId) {
    const params = new URLSearchParams();
    if (learnerId) params.set("learner_id", learnerId);
    if (subjectId) params.set("subject_id", subjectId);
    const q = params.toString() ? `?${params}` : "";
    return request(`/api/journey${q}`);
  },
  insights(id) {
    return request(`/api/sessions/${encodeURIComponent(id)}/insights`);
  },
  journey(id) {
    return request(`/api/sessions/${encodeURIComponent(id)}/journey`);
  },
  startDemo() {
    return request("/api/demo", { method: "POST", headers, body: JSON.stringify({}) });
  },
  demoStep(id) {
    return request(`/api/demo/${encodeURIComponent(id)}/step`, {
      method: "POST",
      headers,
      body: JSON.stringify({}),
    });
  },
  counterfactual() {
    return request("/api/demo/counterfactual", {
      method: "POST",
      headers,
      body: JSON.stringify({}),
    });
  },
  content() {
    return request("/api/content");
  },
  health() {
    return request("/api/health");
  },
  reset(id) {
    return request(`/api/sessions/${encodeURIComponent(id)}/reset`, {
      method: "POST",
      headers,
      body: JSON.stringify({}),
    });
  },
};
