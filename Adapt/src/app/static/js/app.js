import { api } from "./services/api.js";
import { errorMessage, setState, state, subscribe } from "./state/store.js";

const root = document.getElementById("app");
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const STORAGE_KEY = "adapt-session";
const LEARNER_KEY = "adapt-learner";

function el(html) {
  const template = document.createElement("template");
  template.innerHTML = html.trim();
  return template.content;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function learnerId() {
  if (state.learnerId) return state.learnerId;
  try {
    let id = localStorage.getItem(LEARNER_KEY);
    if (!id) {
      id = `learner-${Math.random().toString(16).slice(2, 10)}`;
      localStorage.setItem(LEARNER_KEY, id);
    }
    setState({ learnerId: id });
    return id;
  } catch {
    return "learner-local";
  }
}

function persistSession() {
  try {
    if (!state.session?.session_id) {
      sessionStorage.removeItem(STORAGE_KEY);
      return;
    }
    sessionStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        session_id: state.session.session_id,
        screen: state.screen,
        researchOpen: state.researchOpen,
      })
    );
  } catch {
    /* private mode */
  }
}

function readPersisted() {
  try {
    return JSON.parse(sessionStorage.getItem(STORAGE_KEY) || "null");
  } catch {
    return null;
  }
}

function navLink(hash, label, screen) {
  const current = state.screen === screen || (screen === "learn" && (state.screen === "subjects" || state.screen === "topics"));
  return `<a href="#${hash}" ${current ? 'aria-current="page"' : ""}>${escapeHtml(label)}</a>`;
}

function topbar(session) {
  const progress = session?.progress;
  const label = progress ? `${progress.completed + (session.complete ? 0 : 1)} / ${progress.total}` : "";
  const width = progress ? Math.round((progress.completed / progress.total) * 100) : 0;
  const demo = session?.demo_label || state.demo?.label;
  const theme = session?.theme?.theme || state.subject?.theme?.theme || "";
  return `
    <header class="topbar ${state.navOpen ? "nav-open" : ""}" ${theme ? `data-theme="${escapeHtml(theme)}"` : ""}>
      <a class="brand" href="#landing">ADAPT</a>
      <button class="nav-toggle" type="button" data-action="toggle-nav" aria-expanded="${state.navOpen ? "true" : "false"}">Menu</button>
      <nav class="nav" aria-label="Product">
        ${navLink("learn", "Learn", "learn")}
        ${navLink("progress", "Progress", "progress")}
        ${navLink("journey", "Journey", "journey")}
        ${navLink("how-it-works", "How ADAPT Works", "architecture")}
      </nav>
      <div class="top-actions">
        ${demo ? `<span class="demo-tag">${escapeHtml(demo)}</span>` : ""}
        ${
          progress
            ? `<div class="progress-track" aria-hidden="true"><div class="progress-fill" style="width:${width}%"></div></div>
               <p class="progress-label">Question ${escapeHtml(label)}</p>`
            : ""
        }
        <button class="btn-ghost" type="button" data-action="toggle-research">${
          state.researchOpen ? "Hide research" : "Research mode"
        }</button>
        ${session ? `<button class="btn-ghost" type="button" data-action="reset">Reset</button>` : ""}
      </div>
    </header>
  `;
}

function errorBanner() {
  if (!state.error) return "";
  return `<div class="banner error" role="alert">${escapeHtml(state.error)}</div>`;
}

function chainGraphic(raw) {
  const items = raw && raw.length ? raw : ["Answer", "Evidence", "Learner State", "Strategy", "Next Challenge"];
  const nodes = items
    .map(
      (item, index) =>
        `<li><span>${escapeHtml(item)}</span>${index < items.length - 1 ? `<span class="arrow" aria-hidden="true">↓</span>` : ""}</li>`
    )
    .join("");
  return `<ol class="adapt-chain">${nodes}</ol>`;
}

function masteryBar(percent) {
  if (percent === null || percent === undefined) {
    return `<div class="meter empty"><span class="meter-fill" style="width:0"></span></div><p class="meter-label">New</p>`;
  }
  const width = Math.max(0, Math.min(100, Number(percent)));
  return `<div class="meter" aria-hidden="true"><span class="meter-fill" style="width:${width}%"></span></div><p class="meter-label">${width}%</p>`;
}

function domainVisual(kind) {
  const visuals = {
    qubit: `<svg viewBox="0 0 280 120" role="img" aria-label="A qubit as a two-level system"><circle cx="70" cy="60" r="28" fill="none" stroke="currentColor" stroke-width="3"/><text x="70" y="66" text-anchor="middle" font-size="18">|0⟩</text><circle cx="210" cy="60" r="28" fill="none" stroke="currentColor" stroke-width="3"/><text x="210" y="66" text-anchor="middle" font-size="18">|1⟩</text><path d="M110 60 H170" stroke="currentColor" stroke-width="2" stroke-dasharray="4 4"/></svg>`,
    superposition: `<svg viewBox="0 0 280 120" role="img" aria-label="Superposition of zero and one"><circle cx="140" cy="60" r="36" fill="none" stroke="currentColor" stroke-width="3"/><text x="140" y="55" text-anchor="middle" font-size="16">α|0⟩</text><text x="140" y="78" text-anchor="middle" font-size="16">+ β|1⟩</text></svg>`,
    measurement: `<svg viewBox="0 0 280 120" role="img" aria-label="Measurement giving one definite result"><circle cx="70" cy="60" r="26" fill="none" stroke="currentColor" stroke-width="3"/><text x="70" y="66" text-anchor="middle" font-size="14">ψ</text><path d="M110 60 L170 60 L155 50 M170 60 L155 70" fill="none" stroke="currentColor" stroke-width="3"/><rect x="186" y="36" width="56" height="48" rx="8" fill="none" stroke="currentColor" stroke-width="3"/><text x="214" y="66" text-anchor="middle" font-size="16">0/1</text></svg>`,
    bloch: `<svg viewBox="0 0 280 140" role="img" aria-label="Bloch-sphere inspired picture of a qubit"><ellipse cx="140" cy="72" rx="70" ry="28" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="140" cy="72" r="48" fill="none" stroke="currentColor" stroke-width="2"/><line x1="140" y1="24" x2="140" y2="120" stroke="currentColor" stroke-width="2"/><text x="140" y="18" text-anchor="middle" font-size="14">|0⟩</text><text x="140" y="136" text-anchor="middle" font-size="14">|1⟩</text></svg>`,
    hadamard: `<svg viewBox="0 0 280 110" role="img" aria-label="Hadamard gate on a qubit wire"><line x1="20" y1="55" x2="260" y2="55" stroke="currentColor" stroke-width="3"/><rect x="110" y="28" width="60" height="54" rx="6" fill="none" stroke="currentColor" stroke-width="3"/><text x="140" y="62" text-anchor="middle" font-size="22">H</text></svg>`,
    entanglement: `<svg viewBox="0 0 280 120" role="img" aria-label="Two entangled qubits"><circle cx="80" cy="60" r="24" fill="none" stroke="currentColor" stroke-width="3"/><circle cx="200" cy="60" r="24" fill="none" stroke="currentColor" stroke-width="3"/><path d="M104 60 C140 20 160 100 176 60" fill="none" stroke="currentColor" stroke-width="3"/></svg>`,
    circuit: `<svg viewBox="0 0 280 120" role="img" aria-label="A simple quantum circuit"><line x1="20" y1="40" x2="260" y2="40" stroke="currentColor" stroke-width="3"/><line x1="20" y1="84" x2="260" y2="84" stroke="currentColor" stroke-width="3"/><rect x="70" y="22" width="36" height="36" fill="none" stroke="currentColor" stroke-width="3"/><text x="88" y="46" text-anchor="middle">H</text><circle cx="160" cy="40" r="8" fill="currentColor"/><line x1="160" y1="40" x2="160" y2="84" stroke="currentColor" stroke-width="3"/><circle cx="160" cy="84" r="12" fill="none" stroke="currentColor" stroke-width="3"/></svg>`,
    teleport: `<svg viewBox="0 0 280 120" role="img" aria-label="Teleportation uses entanglement and ordinary communication"><circle cx="50" cy="60" r="16" fill="none" stroke="currentColor" stroke-width="3"/><path d="M70 60 H120" stroke="currentColor" stroke-width="2"/><rect x="120" y="42" width="40" height="36" fill="none" stroke="currentColor" stroke-width="3"/><path d="M160 60 H210" stroke="currentColor" stroke-width="2" stroke-dasharray="5 4"/><circle cx="230" cy="60" r="16" fill="none" stroke="currentColor" stroke-width="3"/></svg>`,
    interference: `<svg viewBox="0 0 280 110" role="img" aria-label="Amplitudes can add or cancel"><path d="M20 55 Q70 10 120 55 T220 55 T270 55" fill="none" stroke="currentColor" stroke-width="3"/><path d="M20 55 Q70 100 120 55 T220 55 T270 55" fill="none" stroke="currentColor" stroke-width="3" opacity="0.55"/></svg>`,
    algorithm: `<svg viewBox="0 0 280 110" role="img" aria-label="A quantum algorithm as a sequence of steps"><rect x="20" y="36" width="70" height="40" rx="8" fill="none" stroke="currentColor" stroke-width="3"/><rect x="105" y="36" width="70" height="40" rx="8" fill="none" stroke="currentColor" stroke-width="3"/><rect x="190" y="36" width="70" height="40" rx="8" fill="none" stroke="currentColor" stroke-width="3"/><text x="55" y="62" text-anchor="middle" font-size="12">setup</text><text x="140" y="62" text-anchor="middle" font-size="12">oracle</text><text x="225" y="62" text-anchor="middle" font-size="12">measure</text></svg>`,
    qec: `<svg viewBox="0 0 280 110" role="img" aria-label="Protecting a logical qubit with extra qubits"><circle cx="140" cy="55" r="18" fill="none" stroke="currentColor" stroke-width="3"/><circle cx="70" cy="55" r="12" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="210" cy="55" r="12" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="140" cy="20" r="12" fill="none" stroke="currentColor" stroke-width="2"/></svg>`,
    code: `<svg viewBox="0 0 280 90" role="img" aria-label="A code snippet"><rect x="16" y="16" width="248" height="58" rx="10" fill="none" stroke="currentColor" stroke-width="2"/><text x="36" y="52" font-family="monospace" font-size="16">for (x in data)</text></svg>`,
    equation: `<svg viewBox="0 0 280 90" role="img" aria-label="A mathematical relationship"><text x="140" y="55" text-anchor="middle" font-size="28">ax + b = c</text></svg>`,
    graph: `<svg viewBox="0 0 280 120" role="img" aria-label="A simple changing quantity"><polyline points="30,90 80,70 130,40 180,50 240,20" fill="none" stroke="currentColor" stroke-width="3"/><line x1="30" y1="100" x2="250" y2="100" stroke="currentColor"/><line x1="30" y1="100" x2="30" y2="16" stroke="currentColor"/></svg>`,
    molecule: `<svg viewBox="0 0 280 110" role="img" aria-label="A simple molecular sketch"><circle cx="90" cy="55" r="16" fill="none" stroke="currentColor" stroke-width="3"/><circle cx="150" cy="55" r="16" fill="none" stroke="currentColor" stroke-width="3"/><circle cx="210" cy="55" r="16" fill="none" stroke="currentColor" stroke-width="3"/><line x1="106" y1="55" x2="134" y2="55" stroke="currentColor" stroke-width="3"/><line x1="166" y1="55" x2="194" y2="55" stroke="currentColor" stroke-width="3"/></svg>`,
    scale: `<svg viewBox="0 0 280 110" role="img" aria-label="A scale comparison"><circle cx="70" cy="70" r="12" fill="none" stroke="currentColor" stroke-width="3"/><circle cx="190" cy="55" r="36" fill="none" stroke="currentColor" stroke-width="3"/><text x="70" y="100" text-anchor="middle" font-size="12">Earth</text><text x="190" y="104" text-anchor="middle" font-size="12">Sun</text></svg>`,
    diagram: `<svg viewBox="0 0 280 110" role="img" aria-label="A physical relationship"><line x1="40" y1="80" x2="240" y2="80" stroke="currentColor" stroke-width="3"/><polygon points="80,80 160,30 160,80" fill="none" stroke="currentColor" stroke-width="3"/></svg>`,
  };
  return visuals[kind] || "";
}

function landing() {
  const content = state.content;
  const learnerChain = content?.product_loop || ["Choose", "Learn", "Answer", "ADAPT notices", "Adaptation", "Improve"];
  const cards = subjectCards(state.subjects || []);
  return `
    ${topbar(null)}
    <main id="main" data-screen="landing">
      ${errorBanner()}
      <section class="hero">
        <p class="kicker">ADAPT</p>
        <h1>Learn differently.</h1>
        <p class="lede">ADAPT changes what you learn next based on how you learn.</p>
        <p class="tagline">A tutor that adapts to how you learn, not just whether you are right.</p>
        <p class="muted">Learn differently with ADAPT. An adaptive tutor that changes what you learn next based on how you learn.</p>
        <div class="cta-row">
          <button class="btn" type="button" data-action="start">Start Learning</button>
          <button class="btn btn-secondary" type="button" data-action="explore">See How ADAPT Works</button>
        </div>
      </section>
      <section class="how-it-adapts" data-screen="explore">
        <div class="explore-head">
          <div>
            <p class="kicker">Explore a subject</p>
            <h2>What do you want to explore?</h2>
          </div>
        </div>
        <div class="subject-grid">${cards || "<p class='loading'>Loading subjects…</p>"}</div>
        ${chainGraphic(learnerChain)}
        <p class="muted">ADAPT notices how you answer, then changes what happens next.</p>
      </section>
    </main>
  `;
}

function subjectCards(list) {
  return (list || [])
    .map((subject) => {
      const percent = subject.mastery_percent;
      const action = subject.action_label || (percent == null ? "Start" : "Continue");
      const status = subject.honesty_label || subject.status_label || (percent == null ? "New" : "In progress");
      return `
        <button class="subject-card" type="button" data-action="choose-subject" data-subject="${escapeHtml(subject.subject_id)}" aria-label="${escapeHtml(subject.name)}">
          <span class="subject-icon" aria-hidden="true">${escapeHtml(subject.icon)}</span>
          <span class="subject-name">${escapeHtml(subject.name)}</span>
          <span class="subject-blurb">${escapeHtml(subject.blurb || "")}</span>
          <span class="subject-meta">${subject.concept_count || 0} concepts</span>
          ${masteryBar(percent)}
          <span class="status-chip ${escapeHtml((subject.status_label || "new").toLowerCase().replace(" ", "_"))}">${escapeHtml(status)}</span>
          <span class="muted">${escapeHtml(action)}</span>
        </button>
      `;
    })
    .join("");
}

function subjects() {
  const cards = subjectCards(state.subjects || []);
  return `
    ${topbar(null)}
    <main id="main" data-screen="subjects">
      ${errorBanner()}
      <p class="kicker">Learn</p>
      <h1>What do you want to explore?</h1>
      <p class="lede">Choose a subject. ADAPT will change what comes next based on how you answer.</p>
      <div class="subject-grid">${cards || "<p class='loading'>Loading subjects…</p>"}</div>
    </main>
  `;
}

function topics() {
  const subject = state.subject;
  if (!subject) return subjects();
  const theme = subject.theme?.theme || subject.subject_id;
  const cards = (subject.concepts || [])
    .map((concept) => {
      const percent = concept.progress_percent;
      const status = concept.status_label || "New";
      return `
        <button class="concept-card" type="button" data-action="choose-concept" data-concept="${escapeHtml(concept.concept_id)}" data-topic="${escapeHtml(concept.topic_id)}" data-subject="${escapeHtml(subject.subject_id)}">
          <span class="concept-name">${escapeHtml(concept.name)}</span>
          <span class="concept-blurb">${escapeHtml(concept.description || "")}</span>
          <span class="concept-meta">${escapeHtml(concept.difficulty_label || concept.tier || "")}</span>
          ${concept.recommended ? `<span class="rec-chip">Recommended</span>` : ""}
          <span class="status-chip ${escapeHtml(concept.status || "new")}">${escapeHtml(concept.honesty_label || status)}</span>
          ${masteryBar(percent)}
          <span class="muted">${escapeHtml(concept.action_label || "Start learning")}</span>
        </button>
      `;
    })
    .join("");
  return `
    ${topbar(null)}
    <main id="main" data-theme="${escapeHtml(theme)}" data-screen="concepts">
      ${errorBanner()}
      <p class="kicker">${escapeHtml(subject.icon || "")} ${escapeHtml(subject.name)}</p>
      <h1>${escapeHtml(subject.name)}</h1>
      <p class="lede">${escapeHtml(subject.blurb || "")}</p>
      <div class="concept-grid">${cards}</div>
      <div class="form-actions">
        <button class="btn-ghost" type="button" data-action="start">All subjects</button>
      </div>
    </main>
  `;
}

function answerControls(session) {
  const challenge = session.challenge || {};
  const choices = challenge.choices || [];
  if (choices.length) {
    return `
      <fieldset class="choices">
        <legend class="sr-only">Your answer</legend>
        ${choices
          .map(
            (choice) => `
              <label class="choice">
                <input type="radio" name="answer" value="${escapeHtml(choice)}" required />
                <span>${escapeHtml(choice)}</span>
              </label>
            `
          )
          .join("")}
      </fieldset>
    `;
  }
  return `
    <label for="answer">Your answer</label>
    <input id="answer" name="answer" type="text" required autocomplete="off" maxlength="20000" />
  `;
}

function approachControls(plan) {
  const options = plan?.approach_options || [];
  if (!options.length) return "";
  return `
    <fieldset class="approach">
      <legend>How did you approach this?</legend>
      <p class="muted">Optional — this helps ADAPT understand your thinking.</p>
      ${options
        .map(
          (item) => `
            <label class="chip">
              <input type="radio" name="approach" value="${escapeHtml(item.id)}" />
              <span>${escapeHtml(item.label)}</span>
            </label>
          `
        )
        .join("")}
    </fieldset>
  `;
}

function confidenceControls(session) {
  const scale = session.evidence_plan?.confidence_quick || [];
  const items = scale.length
    ? scale
    : [
        { value: 1, label: "Not sure", emoji: "😕" },
        { value: 3, label: "Somewhat", emoji: "🙂" },
        { value: 5, label: "Very confident", emoji: "😎" },
      ];
  return `
    <fieldset class="confidence" role="radiogroup" aria-labelledby="confidence-label">
      <legend id="confidence-label">How confident are you?</legend>
      ${items
        .map(
          (item) => `
            <label class="chip confidence-chip">
              <input type="radio" name="confidence" value="${item.value}" required />
              <span class="confidence-emoji" aria-hidden="true">${item.emoji || ""}</span>
              <span class="confidence-copy">${escapeHtml(item.label)}</span>
            </label>
          `
        )
        .join("")}
    </fieldset>
  `;
}

function challengeVisual(session) {
  const presentation = session.presentation || session.challenge?.presentation || {};
  const svg = domainVisual(presentation.visual);
  if (!svg) return "";
  return `<div class="challenge-visual">${svg}</div>`;
}

function challengeScreen(session) {
  const challenge = session.challenge;
  if (!challenge) return `<p>This session is complete.</p>`;
  if (challenge.unavailable) {
    return `<div class="banner error" role="alert">A challenge isn’t available right now.</div>`;
  }
  const disabled = state.submitting ? "disabled" : "";
  const topic = session.topic || {};
  const plan = session.evidence_plan || {};
  const progress = session.progress || {};
  const prompt = challenge.prompt_display || challenge.prompt;
  const codeLike = session.presentation?.code_like;
  return `
    <form class="card challenge-card" id="challenge-form" data-screen="challenge">
      <p class="kicker">${escapeHtml(topic.name || "")}</p>
      <p class="progress-label">Question ${escapeHtml(String(progress.current || 1))} / ${escapeHtml(String(progress.total || 10))}</p>
      ${challengeVisual(session)}
      <h2 class="challenge-prompt ${codeLike ? "prompt-code" : "prompt-math"}">${escapeHtml(prompt)}</h2>
      ${answerControls(session)}
      ${confidenceControls(session)}
      ${approachControls(plan)}
      <details class="optional-explain">
        <summary>Want to explain?</summary>
        <label class="sr-only" for="reasoning">Optional explanation</label>
        <textarea id="reasoning" name="explanation" ${disabled} maxlength="20000" placeholder="${escapeHtml(plan.reasoning_help || "Optional — this helps ADAPT understand your thinking.")}"></textarea>
      </details>
      <div class="form-actions">
        <button class="btn" type="submit" ${disabled}>${state.submitting ? "ADAPT is thinking…" : "Check Answer"}</button>
      </div>
    </form>
  `;
}

function adaptationView(view) {
  if (!view) return "";
  const moment = view.moment || {};
  const doing = view.doing?.text || "";
  const copy = view.moment_copy || view.why_next || "";
  return `
    <section class="card" data-screen="adaptation">
      <p class="kicker">Adaptation</p>
      <div class="moment" aria-label="How ADAPT adapted">
        <div class="moment-step"><strong>YOUR RESPONSE</strong><span>${escapeHtml(view.noticed?.text || "")}</span></div>
        <span class="arrow" aria-hidden="true">↓</span>
        <div class="moment-step"><strong>ADAPT NOTICED</strong><span>${escapeHtml(doing)}</span></div>
        <span class="arrow" aria-hidden="true">↓</span>
        <div class="moment-step"><strong>YOUR NEXT STEP</strong><span>${escapeHtml(view.next?.text || copy)}</span></div>
      </div>
      <p>${escapeHtml(copy)}</p>
    </section>
  `;
}

function feedbackScreen(session) {
  const result = state.result || session.last_result;
  if (!result) return challengeScreen(session);
  const feedback = result.feedback || {};
  const explanation = result.explanation || {};
  const noticed = result.noticed;
  const why = result.why_this_question;
  const passed = feedback.answer_status === "CORRECT";
  const headline = explanation.headline || (passed ? "Nice work." : "Not quite.");
  const short = explanation.short_message || noticed?.summary || feedback.detail || "";
  const detailed = explanation.detailed_message || "";
  const noticedBody = noticed?.body || noticed?.headline || noticed?.summary || explanation.noticed || "";
  return `
    <section class="card feedback-card" data-tone="${escapeHtml(feedback.tone)}" data-screen="feedback" aria-live="polite">
      <p class="kicker">Result</p>
      <h2>${passed ? "Nice work." : escapeHtml(headline)}</h2>
      <p>${escapeHtml(short)}</p>
      ${
        detailed && detailed !== short
          ? `<details class="optional-explain" ${state.detailOpen ? "open" : ""}>
               <summary>Show more</summary>
               <p>${escapeHtml(detailed)}</p>
             </details>`
          : ""
      }
    </section>
    <section class="card noticed-card feedback-block" data-screen="noticed">
      <h3>✦ What ADAPT noticed</h3>
      <p>${escapeHtml(noticedBody)}</p>
    </section>
    <section class="card feedback-block" data-screen="why">
      <h3>Why this question?</h3>
      <p>${escapeHtml(why?.text || explanation.why_next || "")}</p>
    </section>
    ${adaptationView(result.adaptation_view)}
    <div class="form-actions">
      <button class="btn" type="button" data-action="${session.complete ? "summary" : "continue"}">
        ${session.complete ? "See session summary" : "Continue"}
      </button>
    </div>
  `;
}

function sessionScreen() {
  const session = state.session;
  if (!session) return landing();
  const theme = session.theme?.theme || "";
  const body = state.screen === "feedback" ? feedbackScreen(session) : challengeScreen(session);
  return `
    ${topbar(session)}
    <main id="main" class="narrow" ${theme ? `data-theme="${escapeHtml(theme)}"` : ""}>
      ${errorBanner()}
      <p class="sr-status" aria-live="polite">${state.submitting ? "ADAPT is analyzing your response." : ""}</p>
      ${body}
      ${state.researchOpen ? researchPanel() : ""}
    </main>
  `;
}

function researchPanel() {
  const chain = state.trace?.chain || [];
  const last = chain[chain.length - 1];
  const timeline = (state.trace?.timeline || [])
    .filter((item) => item.step > 0)
    .map((item) => `<span class="pill">Step ${item.step} ${escapeHtml(item.strategy)}</span>`)
    .join("");
  if (!last) {
    return `<section class="research-panel"><h2>Research mode</h2><p>No steps yet. Submit an answer to see evidence → state → strategy → challenge.</p></section>`;
  }
  const explain = last.human_explanation || last.adaptation?.explanation || {};
  const rs = last.state;
  return `
    <section class="research-panel" aria-label="ADAPT research trace">
      <h2>Research mode</h2>
      <p class="muted">Evidence → Learner State → Strategy → Next Challenge</p>
      <div class="chain">
        <div class="chain-step"><span class="mark">↓</span><div><strong>Evidence</strong><br>${escapeHtml(explain.evidence || last.evidence.answer_status)}<br><span class="dim">${escapeHtml(explain.evidence_detail || "")}</span></div></div>
        <div class="chain-step"><span class="mark">↓</span><div><strong>Learner State</strong><br>Mastery: ${rs.mastery} ${rs.mastery_arrow} · Confidence: ${rs.confidence} ${rs.confidence_arrow}<br><span class="dim">${escapeHtml(explain.state || "")}</span></div></div>
        <div class="chain-step"><span class="mark">↓</span><div><strong>Strategy</strong><br>${escapeHtml(explain.strategy_label || last.strategy.decision)}<br><span class="dim">${escapeHtml(explain.strategy || last.strategy.reason)}</span></div></div>
        <div class="chain-step"><span class="mark">↓</span><div><strong>Next Challenge</strong><br>${escapeHtml(last.next_challenge.challenge_id)} · ${escapeHtml(last.next_challenge.challenge_type || "")}<br><span class="dim">${escapeHtml(explain.next_challenge || "")}</span></div></div>
      </div>
      <h3>Timeline</h3>
      <div class="timeline">${timeline}</div>
    </section>
  `;
}

function summaryScreen() {
  const summary = state.summary;
  if (!summary) return `<p class="loading">Loading summary…</p>`;
  const insights = summary.insights || state.insights || {};
  return `
    ${topbar(state.session)}
    <main id="main" class="narrow">
      ${errorBanner()}
      <section class="card">
        <p class="kicker">Session complete</p>
        <h1>${escapeHtml(summary.title)}</h1>
        <dl class="summary-grid">
          <dt>Challenges completed</dt><dd>${summary.challenges_completed}</dd>
          <dt>Concepts explored</dt><dd>${summary.concepts_explored}</dd>
          <dt>ADAPT adjusted your path</dt><dd>${summary.adapt_adjusted_path} times</dd>
        </dl>
        ${insights.good_at ? `<p><strong>What you're good at.</strong> ${escapeHtml(insights.good_at)}</p>` : ""}
        ${insights.practice ? `<p><strong>Areas to practice.</strong> ${escapeHtml(insights.practice)}</p>` : ""}
        ${insights.how_you_learn ? `<p><strong>How you learn.</strong> ${escapeHtml(insights.how_you_learn)}</p>` : ""}
        ${insights.recent_change ? `<p><strong>Recent change.</strong> ${escapeHtml(insights.recent_change)}</p>` : ""}
        <div class="cta-row" style="justify-content:flex-start">
          <button class="btn" type="button" data-action="start">Start Learning</button>
          <button class="btn btn-secondary" type="button" data-action="journey">Learning journey</button>
          <button class="btn btn-secondary" type="button" data-action="progress">Your progress</button>
          <button class="btn btn-secondary" type="button" data-action="reset">Reset</button>
        </div>
      </section>
      ${state.researchOpen ? researchPanel() : ""}
    </main>
  `;
}

function progressScreen() {
  const progress = state.progress;
  if (!progress) return `<p class="loading">Loading progress…</p>`;
  const overall = progress.overall_available
    ? `<div class="overall">${masteryBar(progress.overall_percent)}<p>Visit progress</p></div>`
    : `<p class="muted">No recorded progress yet. Start a subject to see an honest picture of this visit.</p>`;
  const subjects = (progress.subjects || [])
    .map((subject) => {
      const pct = subject.mastery_percent;
      return `<div class="progress-row"><span>${escapeHtml(subject.icon)} ${escapeHtml(subject.name)} · ${escapeHtml(subject.honesty_label || subject.status_label || "")}</span>${masteryBar(pct)}</div>`;
    })
    .join("");
  const concepts = (progress.concept_map || [])
    .map((item) => `<div class="progress-row"><span>${escapeHtml(item.name)} · ${escapeHtml(item.status_label || "New")}</span>${masteryBar(item.progress_percent ?? item.mastery_percent)}</div>`)
    .join("");
  const attention = (progress.areas_needing_attention || [])
    .map((item) => `<li>${escapeHtml(item.name)}</li>`)
    .join("");
  const improving = (progress.areas_improving || [])
    .map((item) => `<li>${escapeHtml(item.name)}</li>`)
    .join("");
  return `
    ${topbar(state.session)}
    <main id="main" class="narrow">
      <p class="kicker">Progress</p>
      <h1>Your Journey</h1>
      ${overall}
      <p class="muted">Challenges completed this visit: ${escapeHtml(String(progress.challenges_completed || 0))}</p>
      <h2>Subjects explored</h2>
      <div class="stack">${subjects}</div>
      ${concepts ? `<h2>Concepts practiced</h2><div class="stack">${concepts}</div>` : ""}
      ${attention ? `<h2>Areas needing attention</h2><ul>${attention}</ul>` : ""}
      ${improving ? `<h2>Areas improving</h2><ul>${improving}</ul>` : ""}
      <p class="muted">${escapeHtml(progress.disclaimer || "")}</p>
      <div class="form-actions">
        <button class="btn" type="button" data-action="start">Continue learning</button>
        ${state.session ? `<button class="btn-ghost" type="button" data-action="continue-session">Back to challenge</button>` : ""}
      </div>
    </main>
  `;
}

function insightsScreen() {
  const insights = state.insights || {};
  return `
    ${topbar(state.session)}
    <main id="main" class="narrow">
      <p class="kicker">Insights</p>
      <h1>Learning insights</h1>
      <section class="card">
        ${(insights.lines || []).map((line) => `<p class="insight-line">✦ ${escapeHtml(line)}</p>`).join("") || ""}
        <h2>What you're good at</h2>
        <p>${escapeHtml(insights.good_at || "Not enough recorded evidence yet.")}</p>
        <h2>Areas to practice</h2>
        <p>${escapeHtml(insights.practice || "Not enough recorded evidence yet.")}</p>
        <h2>How you learn</h2>
        <p>${escapeHtml(insights.how_you_learn || "Not enough recorded evidence yet.")}</p>
        <h2>Recent change</h2>
        <p>${escapeHtml(insights.recent_change || "Not enough recorded evidence yet.")}</p>
      </section>
      <div class="form-actions">
        <button class="btn" type="button" data-action="progress">Back to progress</button>
      </div>
    </main>
  `;
}

function journeyScreen() {
  const journey = state.journey || state.summary?.journey || {};
  const catalog = journey.catalog || (journey.steps && journey.steps[0]?.kind === "concept" ? journey : null);
  const stages = journey.stages || [];
  const stageItems = stages
    .map(
      (step, index) => `
        <div class="journey-step" data-status="${escapeHtml(step.status || "")}">
          <span class="journey-marker" aria-hidden="true">${escapeHtml(step.marker || "○")}</span>
          <span><strong>${escapeHtml(step.name)}</strong></span>
        </div>
        ${index < stages.length - 1 ? `<span class="arrow" aria-hidden="true">↓</span>` : ""}
      `
    )
    .join("");
  const display = catalog?.steps || journey.steps || [];
  const items = display
    .map((step, index) => {
      const marker = step.marker || step.status || "new";
      const symbol = marker === "completed" || step.status === "completed" ? "✓" : marker === "in_progress" || step.status === "in_progress" ? "→" : marker === "recommended" ? "★" : "○";
      return `
        <button class="journey-step" type="button" data-action="journey-step" data-index="${index}" data-status="${escapeHtml(step.status || "")}" data-marker="${escapeHtml(marker)}">
          <span class="journey-marker" aria-hidden="true">${symbol}</span>
          <span>
            <strong>${escapeHtml(step.name || step.label || step.strategy || "")}</strong>
            <span class="muted"> ${escapeHtml(step.status_label || "")}</span>
          </span>
        </button>
      `;
    })
    .join("");
  const selected = state.journeyStep;
  const detail = selected
    ? `<section class="card">
        <h2>${escapeHtml(selected.name || selected.strategy || "")}</h2>
        <p>${escapeHtml(selected.description || selected.noticed || selected.evidence || "")}</p>
        <p class="muted">${escapeHtml(selected.strategy_text || selected.status_label || "")}</p>
      </section>`
    : "";
  return `
    ${topbar(state.session)}
    <main id="main" class="narrow">
      <p class="kicker">Journey</p>
      <h1>Your Journey</h1>
      ${stageItems ? `<div class="journey">${stageItems}</div>` : ""}
      <div class="journey">${items || "<p class='muted'>Start a subject to see your path.</p>"}</div>
      ${detail}
      <p class="muted">${escapeHtml(catalog?.disclaimer || journey.disclaimer || "")}</p>
      <div class="form-actions">
        <button class="btn" type="button" data-action="start">Start Learning</button>
      </div>
    </main>
  `;
}

function storyScreen() {
  return journeyScreen();
}

function counterfactualScreen() {
  const cf = state.counterfactual;
  if (!cf) {
    return `
      ${topbar(null)}
      <main id="main" class="narrow">
        <p class="loading">Running both learners through AdaptiveTutor…</p>
      </main>
    `;
  }
  const card = (learner, evidence) => `
    <article class="card">
      <h2>${escapeHtml(learner.label)}</h2>
      <p>${escapeHtml(learner.evidence_summary || evidence)}</p>
      <p class="decision">${escapeHtml(state.researchOpen ? learner.final_decision_label || learner.final_decision : learner.final_decision_plain || learner.final_decision_label || "—")}</p>
      ${state.researchOpen ? `<p>Next challenge: ${escapeHtml(learner.final_challenge || "—")}</p>` : ""}
    </article>
  `;
  const chain = cf.chain || ["Same start", "Different evidence", "Different state", "Different strategy", "Different challenge"];
  return `
    ${topbar(null)}
    <main id="main">
      <p class="kicker">${escapeHtml(cf.label || "DEMO SCENARIO")}</p>
      <h1>Same starting point</h1>
      <p class="lede">${escapeHtml(cf.headline || "Different evidence. Different decision.")}</p>
      <p class="muted">Same start + different evidence = different adaptation.</p>
      <div class="split">
        ${card(cf.learner_a, "Strong reasoning. High confidence.")}
        ${card(cf.learner_b, "Weak reasoning. Low confidence.")}
      </div>
      ${chainGraphic(chain)}
      <p class="banner info">${cf.differentiated ? "Same start. Different evidence. Different strategy. Different challenge." : "The two paths did not differentiate."}</p>
      <div class="form-actions">
        <button class="btn" type="button" data-action="start">Start Learning</button>
        <button class="btn btn-secondary" type="button" data-action="toggle-research">${state.researchOpen ? "Hide research" : "Research mode"}</button>
        <button class="btn btn-secondary" type="button" data-action="landing">Home</button>
      </div>
    </main>
  `;
}

function demoScreen() {
  const session = state.session;
  return `
    ${topbar(session)}
    <main id="main" class="narrow">
      ${errorBanner()}
      <p class="kicker">${escapeHtml(state.demo?.label || session?.demo_label || "DEMO SCENARIO")}</p>
      <h1>Watch ADAPT change its mind for a reason.</h1>
      ${state.screen === "feedback" ? feedbackScreen(session || {}) : challengeScreen(session || { challenge: { prompt: "Loading…" }, confidence_scale: [] })}
      ${state.researchOpen ? researchPanel() : ""}
    </main>
  `;
}

function architectureScreen() {
  const items = state.content?.architecture || [];
  const list = items
    .map(
      (item, index) => `
        <li>
          <strong>${escapeHtml(item.name)}</strong>
          <p>${escapeHtml(item.summary)}</p>
          ${index < items.length - 1 ? `<span class="arrow">↓</span>` : ""}
        </li>
      `
    )
    .join("");
  const evidence = state.content?.technical_evidence;
  const phases = (evidence?.phases || [])
    .map(
      (phase) => `
        <article class="card evidence-card">
          <h2>${escapeHtml(phase.title)}</h2>
          <ul>${(phase.items || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
        </article>
      `
    )
    .join("");
  const limits = (state.content?.limitations || [])
    .map(
      (item) => `
        <article class="card">
          <h2>${escapeHtml(item.title)}</h2>
          <p>${escapeHtml(item.detail)}</p>
        </article>
      `
    )
    .join("");
  return `
    ${topbar(null)}
    <main id="main" class="narrow">
      <p class="kicker">How ADAPT Works</p>
      <h1>An adaptive tutor that changes what you learn next based on how you learn.</h1>
      ${chainGraphic(state.content?.chain)}
      <ol class="arch-list">${list}</ol>
      <div class="form-actions">
        <button class="btn" type="button" data-action="start">Start Learning</button>
        <button class="btn btn-secondary" type="button" data-action="demo">Watch the demo</button>
        <button class="btn btn-secondary" type="button" data-action="counterfactual">Counterfactual</button>
      </div>
      <h2>Technical evidence</h2>
      <p class="lede">${escapeHtml(evidence?.disclaimer || "")}</p>
      <div class="stack">${phases}</div>
      <p class="banner info">${escapeHtml(state.content?.phase5?.statement || "Phase 5 human learning evaluation: INCONCLUSIVE (n=0)")}</p>
      <h2>Known limitations</h2>
      <div class="stack">${limits}</div>
      <section class="promise-strip">
        <p>ADAPT doesn't just ask whether you're right. It learns from how you answer and changes what happens next.</p>
      </section>
    </main>
  `;
}

function evidenceScreen() {
  return architectureScreen();
}

function limitationsScreen() {
  return architectureScreen();
}

function render() {
  const screens = {
    landing,
    subjects,
    learn: subjects,
    topics,
    session: sessionScreen,
    feedback: sessionScreen,
    summary: summaryScreen,
    story: storyScreen,
    journey: journeyScreen,
    progress: progressScreen,
    insights: insightsScreen,
    counterfactual: counterfactualScreen,
    demo: demoScreen,
    architecture: architectureScreen,
    evidence: evidenceScreen,
    limitations: limitationsScreen,
  };
  const view = screens[state.screen] || landing;
  root.replaceChildren(el(view()));
  persistSession();
}

async function ensureContent() {
  if (state.content) return state.content;
  try {
    const content = await api.content();
    setState({ content });
    return content;
  } catch {
    return null;
  }
}

async function loadSubjects() {
  setState({ loading: true, error: null, screen: "subjects", navOpen: false });
  try {
    const data = await api.subjects(learnerId());
    setState({ subjects: data.subjects, loading: false });
  } catch (error) {
    setState({ error: errorMessage(error), loading: false });
  }
}

async function loadTopics() {
  return loadSubjects();
}

async function openSubject(subjectId) {
  setState({ loading: true, error: null, screen: "topics", navOpen: false });
  try {
    const subject = await api.subject(subjectId, learnerId());
    setState({ subject, loading: false });
  } catch (error) {
    setState({ error: errorMessage(error), loading: false });
  }
}

async function startTopic(topicId, subjectId, conceptId) {
  setState({ loading: true, error: null });
  try {
    const session = await api.createSession({
      topic_id: topicId,
      subject_id: subjectId,
      concept_id: conceptId,
      learner_id: learnerId(),
      max_steps: 10,
      mode: "learner",
    });
    setState({ session, result: null, trace: null, screen: "session", loading: false, noticedOpen: true, whyOpen: true, detailOpen: false, navOpen: false });
  } catch (error) {
    setState({ error: errorMessage(error), loading: false });
  }
}

async function submitAnswer(form) {
  const session = state.session;
  if (!session || state.submitting) return;
  const data = new FormData(form);
  const answer = String(data.get("answer") || "").trim();
  const confidence = data.get("confidence");
  const approach = data.get("approach");
  const explanation = String(data.get("explanation") || data.get("reasoning") || "").trim();
  if (!answer || !confidence) {
    setState({ error: "Please enter an answer and choose how confident you are." });
    return;
  }
  setState({ submitting: true, error: null });
  try {
    const result = await api.submitResponse(session.session_id, {
      answer,
      confidence: Number(confidence),
      approach: approach || undefined,
      explanation,
      challenge_id: session.challenge?.challenge_id,
    });
    const trace = await api.trace(session.session_id);
    setState({
      session: result,
      result: result.result,
      trace,
      submitting: false,
      screen: "feedback",
      noticedOpen: true,
      whyOpen: true,
      detailOpen: false,
    });
  } catch (error) {
    setState({ submitting: false, error: errorMessage(error) });
  }
}

function continueSession() {
  const session = state.session;
  if (!session) return;
  if (session.complete) {
    showSummary();
    return;
  }
  setState({ screen: "session", result: null, error: null, noticedOpen: true, whyOpen: true, detailOpen: false });
}

async function showSummary() {
  if (!state.session) return;
  try {
    const summary = await api.summary(state.session.session_id);
    const story = await api.story(state.session.session_id);
    const trace = await api.trace(state.session.session_id);
    setState({ summary, story, trace, insights: summary.insights, journey: summary.journey, screen: "summary", error: null });
  } catch (error) {
    setState({ error: errorMessage(error) });
  }
}

async function showProgress() {
  location.hash = "progress";
  try {
    const progress = state.session
      ? await api.progress(state.session.session_id)
      : await api.progressQuery(learnerId());
    setState({ progress, screen: "progress", navOpen: false });
  } catch (error) {
    setState({ error: errorMessage(error) });
  }
}

async function showInsights() {
  if (!state.session) return;
  try {
    const insights = state.insights || (await api.insights(state.session.session_id));
    setState({ insights, screen: "insights" });
  } catch (error) {
    setState({ error: errorMessage(error) });
  }
}

async function showJourney() {
  location.hash = "journey";
  try {
    const journey = state.session
      ? await api.journey(state.session.session_id)
      : await api.journeyQuery(learnerId(), state.subject?.subject_id);
    setState({ journey, screen: "journey", navOpen: false });
  } catch (error) {
    setState({ error: errorMessage(error) });
  }
}

async function showStory() {
  return showJourney();
}

async function runCounterfactual() {
  location.hash = "counterfactual";
  setState({ screen: "counterfactual", loading: true, error: null, counterfactual: null, navOpen: false });
  try {
    const counterfactual = await api.counterfactual();
    setState({ counterfactual, loading: false });
  } catch (error) {
    setState({ error: errorMessage(error), loading: false });
  }
}

async function runDemo() {
  setState({ screen: "demo", loading: true, error: null, researchOpen: true, navOpen: false });
  try {
    const session = await api.startDemo();
    setState({ session, demo: session.demo, loading: false, screen: "demo" });
    await playDemo(session.session_id);
  } catch (error) {
    setState({ error: errorMessage(error), loading: false });
  }
}

async function playDemo(sessionId) {
  const pause = reducedMotion ? 0 : 900;
  for (let i = 0; i < 12; i += 1) {
    await new Promise((resolve) => setTimeout(resolve, pause));
    try {
      const result = await api.demoStep(sessionId);
      const trace = await api.trace(sessionId);
      setState({
        session: result,
        result: result.result,
        trace,
        demo: result.demo,
        screen: "feedback",
      });
      await new Promise((resolve) => setTimeout(resolve, pause));
      if (result.demo?.complete || result.complete) {
        await showSummary();
        return;
      }
      setState({ screen: "session", result: null });
    } catch (error) {
      if (error.code === "session_complete") {
        await showSummary();
        return;
      }
      setState({ error: errorMessage(error) });
      return;
    }
  }
}

async function toggleResearch() {
  const next = !state.researchOpen;
  if (next && state.session) {
    try {
      const trace = await api.trace(state.session.session_id);
      setState({ researchOpen: true, trace });
      return;
    } catch (error) {
      setState({ researchOpen: true, error: errorMessage(error) });
      return;
    }
  }
  setState({ researchOpen: next });
}

async function resetSession() {
  const session = state.session;
  try {
    sessionStorage.removeItem(STORAGE_KEY);
  } catch {
    /* ignore */
  }
  if (!session) {
    goLanding();
    return;
  }
  try {
    const next = await api.reset(session.session_id);
    setState({
      session: next,
      result: null,
      trace: null,
      summary: null,
      story: null,
      demo: next.demo || null,
      error: null,
      screen: next.mode === "demo" ? "demo" : "session",
      researchOpen: next.mode === "demo",
    });
  } catch {
    goLanding();
  }
}

function goLanding() {
  location.hash = "landing";
  setState({
    screen: "landing",
    session: null,
    result: null,
    trace: null,
    summary: null,
    story: null,
    demo: null,
    error: null,
    counterfactual: null,
    navOpen: false,
  });
}

async function showStatic(screen) {
  location.hash = screen === "architecture" ? "how-it-works" : screen;
  await ensureContent();
  setState({ screen, error: null, navOpen: false });
}

root.addEventListener("click", (event) => {
  const button = event.target.closest("[data-action]");
  if (!button) return;
  if (state.submitting && button.getAttribute("data-action") !== "toggle-research") return;
  const action = button.getAttribute("data-action");
  if (action === "start") loadSubjects();
  if (action === "explore") showStatic("architecture");
  if (action === "choose-subject") openSubject(button.getAttribute("data-subject"));
  if (action === "choose-topic") startTopic(button.getAttribute("data-topic"), button.getAttribute("data-subject"));
  if (action === "choose-concept") {
    startTopic(
      button.getAttribute("data-topic"),
      button.getAttribute("data-subject"),
      button.getAttribute("data-concept")
    );
  }
  if (action === "continue" || action === "continue-session") continueSession();
  if (action === "summary") showSummary();
  if (action === "story" || action === "journey") showJourney();
  if (action === "progress") showProgress();
  if (action === "insights") showInsights();
  if (action === "demo") runDemo();
  if (action === "counterfactual") runCounterfactual();
  if (action === "toggle-research") toggleResearch();
  if (action === "toggle-nav") setState({ navOpen: !state.navOpen });
  if (action === "toggle-noticed") setState({ noticedOpen: !state.noticedOpen });
  if (action === "toggle-why") setState({ whyOpen: !state.whyOpen });
  if (action === "journey-step") {
    const index = Number(button.getAttribute("data-index"));
    const journey = state.journey || state.summary?.journey || {};
    const steps = journey.catalog?.steps || journey.steps || [];
    setState({ journeyStep: steps[index] || null, screen: "journey" });
  }
  if (action === "reset") resetSession();
  if (action === "landing") goLanding();
});

root.addEventListener("submit", (event) => {
  if (event.target.id === "challenge-form") {
    event.preventDefault();
    submitAnswer(event.target);
  }
});

window.addEventListener("hashchange", () => {
  const hash = (location.hash || "#landing").replace("#", "");
  if (hash === "landing") goLanding();
  if (hash === "subjects" || hash === "learn") loadSubjects();
  if (hash === "architecture" || hash === "how-it-works") showStatic("architecture");
  if (hash === "evidence") showStatic("evidence");
  if (hash === "limitations") showStatic("limitations");
  if (hash === "progress") showProgress();
  if (hash === "journey") showJourney();
  if (hash === "counterfactual" && !state.counterfactual) runCounterfactual();
});

subscribe(render);
ensureContent().then(async () => {
  learnerId();
  try {
    const data = await api.subjects(learnerId());
    setState({ subjects: data.subjects });
  } catch {
    /* landing can still render */
  }
  const hash = (location.hash || "").replace("#", "");
  if (hash === "architecture" || hash === "evidence" || hash === "limitations" || hash === "how-it-works") {
    setState({ screen: hash === "how-it-works" ? "architecture" : hash || "architecture" });
    return;
  }
  if (hash === "subjects" || hash === "learn") {
    await loadSubjects();
    return;
  }
  if (hash === "progress") {
    await showProgress();
    return;
  }
  if (hash === "journey") {
    await showJourney();
    return;
  }
  const saved = readPersisted();
  if (saved?.session_id) {
    try {
      const session = await api.getSession(saved.session_id);
      const trace = session.progress?.completed ? await api.trace(saved.session_id) : null;
      setState({
        session,
        trace,
        screen: saved.screen === "feedback" ? "feedback" : session.complete ? "summary" : "session",
        researchOpen: Boolean(saved.researchOpen),
        result: session.last_result,
      });
      return;
    } catch {
      sessionStorage.removeItem(STORAGE_KEY);
    }
  }
  render();
});
