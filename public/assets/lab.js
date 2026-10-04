/* Lab page: start a run, stream the lead agent live, and link to the saved report. */
(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const form = $("run-form");
  if (!form) return;

  const STORAGE_KEY = "artemis.activeRun";
  const EVENT_NAMES = [
    "artemis.relay", "session.sandbox_status", "session.status", "turn.started", "turn.completed", "turn.failed",
    "response.created", "response.in_progress", "response.output_text.delta", "response.output_item.added",
    "response.output_item.done", "response.completed", "response.failed", "response.error",
    "response.function_call_arguments.done", "session.usage", "session.title",
  ];
  const statusEl = $("form-status"), feed = $("feed"), meta = $("run-meta");
  const startButton = $("start-button"), stopButton = $("stop-button");
  const actions = $("run-actions"), resultLink = $("result-link");
  let run = null, source = null, current = null, finished = false, started = 0;

  const store = {
    save(value) { try { localStorage.setItem(STORAGE_KEY, JSON.stringify(value)); } catch (_) {} },
    load() { try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || "null"); } catch (_) { return null; } },
    clear() { try { localStorage.removeItem(STORAGE_KEY); } catch (_) {} },
  };

  function say(text, bad) { statusEl.textContent = text; statusEl.className = "form-status" + (bad ? " bad" : ""); }

  function stage(name, state) {
    const order = ["sandbox", "working", "saving", "done"];
    document.querySelectorAll("#stages li").forEach((li) => {
      const idx = order.indexOf(li.dataset.stage), target = order.indexOf(name);
      if (state === "reset") { li.dataset.state = "idle"; return; }
      if (idx < target && li.dataset.state !== "failed") li.dataset.state = "done";
      else if (idx === target) li.dataset.state = state;
    });
  }

  function elapsed() {
    const s = Math.max(0, Math.round((Date.now() - started) / 1000));
    return `${Math.floor(s / 60)} min ${String(s % 60).padStart(2, "0")} s`;
  }

  function clearFeed() { feed.replaceChildren(); }

  function newMessage() {
    const article = document.createElement("article");
    const time = document.createElement("time");
    time.textContent = elapsed();
    const msg = document.createElement("div");
    msg.className = "msg";
    article.append(time, msg);
    feed.appendChild(article);
    current = msg;
    return msg;
  }

  function note(text, cls) {
    const p = document.createElement("article");
    p.innerHTML = '<div class="tool"></div>';
    p.firstChild.textContent = text;
    if (cls) p.firstChild.className = cls;
    feed.appendChild(p);
    feed.scrollTop = feed.scrollHeight;
  }

  function cleanText(text) { return text.replace(/ARTEMIS-RUN-COMPLETE\s*$/m, "").trimEnd(); }

  // While text streams in it is shown plainly; once a message is complete it is
  // rendered as formatted markdown (headings, lists, tables, links).
  function renderCurrent() {
    if (!current || !window.ArtemisMarkdown) return;
    const raw = current.dataset.raw || current.textContent;
    current.innerHTML = window.ArtemisMarkdown.render(cleanText(raw));
    current.classList.add("prose");
    if (window.ArtemisStackTables) window.ArtemisStackTables(current);
  }

  function handle(ev) {
    const type = ev && ev.type;
    if (!type) return;
    if (type === "artemis.relay") {
      if (ev.state === "finished") return finish(ev);
      if (ev.state === "upstream_error") note("The lab server reported a problem with the stream; reconnecting.");
      return;
    }
    if (type === "session.sandbox_status") {
      if (ev.stage === "failed") { stage("sandbox", "failed"); say("The sandbox could not start: " + (ev.error || "unknown reason") + ".", true); return; }
      if (ev.stage === "ready") { stage("working", "active"); meta.textContent = "Sandbox ready. The agents are working."; }
      else meta.textContent = "Sandbox: " + ev.stage + ".";
      return;
    }
    if (type === "response.output_text.delta") {
      stage("working", "active");
      const msg = current || newMessage();
      msg.dataset.raw = (msg.dataset.raw || "") + (ev.delta || "");
      msg.textContent = cleanText(msg.dataset.raw);
      feed.scrollTop = feed.scrollHeight;
      return;
    }
    if (type === "response.output_item.added") {
      const item = ev.item || {};
      if (item.type === "function_call" && item.name) {
        const label = item.name === "sys_session_send" ? "Handing work to a specialist agent" :
          item.name === "sys_read_inbox" ? "Collecting results from the team" : "Using tool: " + item.name;
        note(label);
      }
      return;
    }
    if (type === "turn.completed" || type === "response.completed") { renderCurrent(); current = null; return; }
    if (type === "turn.failed" || type === "response.failed" || type === "response.error") {
      note("The agent reported an error in this step. The lab usually recovers on its own.", "tool");
    }
  }

  function openStream() {
    if (source) source.close();
    const url = `/api/runs/${encodeURIComponent(run.run_id)}/stream?t=${encodeURIComponent(run.token)}`;
    source = new EventSource(url);
    const onMessage = (m) => { try { handle(JSON.parse(m.data)); } catch (_) {} };
    source.onmessage = onMessage;
    EVENT_NAMES.forEach((n) => source.addEventListener(n, onMessage));
    source.onerror = () => { if (finished) source.close(); };
  }

  function finish(ev) {
    renderCurrent();
    finished = true;
    if (source) source.close();
    store.clear();
    stopButton.hidden = true;
    startButton.disabled = false;
    if (ev.outcome === "complete") {
      stage("done", "done");
      document.querySelectorAll("#stages li").forEach((li) => { li.dataset.state = "done"; });
      meta.textContent = "Finished after " + elapsed() + ". The report is saved and published.";
      resultLink.href = ev.result_url || `/results/run?id=${encodeURIComponent(run.run_id)}`;
      resultLink.hidden = false;
      say("Run complete.");
    } else {
      stage("saving", "failed");
      meta.textContent = "The run finished, but saving the report failed. It will be retried automatically within 15 minutes.";
      resultLink.href = "/results"; resultLink.hidden = false; resultLink.textContent = "Go to Results";
    }
  }

  async function start(kind, question, code) {
    say("Creating the lab session.");
    startButton.disabled = true;
    const res = await fetch("/api/runs", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ access_code: code, kind, question }),
    });
    const body = await res.json().catch(() => ({}));
    startButton.blur();
    if (!res.ok) {
      startButton.disabled = false;
      const detail = typeof body.detail === "string" ? body.detail : "The request was not accepted (" + res.status + ").";
      say(detail, true);
      return;
    }
    run = { run_id: body.run_id, token: body.token, kind, question, started: Date.now(), title: body.title };
    store.save(run);
    begin(true, body.typical_minutes, body.saving);
  }

  async function begin(fresh, minutes, saving) {
    started = run.started || Date.now();
    finished = false;
    clearFeed();
    stage("reset", "reset");
    stage("sandbox", "active");
    actions.hidden = false; stopButton.hidden = false; resultLink.hidden = true;
    meta.textContent = fresh
      ? `Started. A sandbox is launching; this takes about 30 seconds. Typical run: ${minutes || "a few"} minutes.` +
        (saving === false ? " Saving is not configured, so copy anything you want to keep." : "")
      : "Reconnected to your run in progress.";
    openStream();
    if (!fresh) { stage("working", "active"); return; }
    say("Sandbox launching. The first message is sent as soon as it is ready.");
    const sent = await fetch(`/api/runs/${encodeURIComponent(run.run_id)}/start?t=${encodeURIComponent(run.token)}`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ kind: run.kind, question: run.question || "" }),
    });
    const ack = await sent.json().catch(() => ({}));
    if (!sent.ok) {
      stage("sandbox", "failed");
      say(typeof ack.detail === "string" ? ack.detail : "The run could not start (" + sent.status + ").", true);
      startButton.disabled = false;
      return;
    }
    stage("working", "active");
    say("Running. You can leave this page; the run continues and is saved when it finishes.");
  }

  // ---------- form ----------
  const questionField = $("question-field");
  const syncKind = () => {
    const kind = form.querySelector("input[name=kind]:checked").value;
    questionField.hidden = kind !== "proposal";
  };
  form.querySelectorAll("input[name=kind]").forEach((r) => r.addEventListener("change", syncKind));
  syncKind();

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const kind = form.querySelector("input[name=kind]:checked").value;
    const question = $("question").value.trim();
    const code = $("access-code").value.trim();
    if (kind === "proposal" && question.length < 15) { say("Please describe your question in at least a sentence.", true); $("question").focus(); return; }
    if (!code) { say("Enter the access code to start a run.", true); $("access-code").focus(); return; }
    start(kind, question, code).catch(() => { startButton.disabled = false; say("The lab could not be reached. Check your connection and try again.", true); });
  });

  stopButton.addEventListener("click", async () => {
    if (!run) return;
    if (!window.confirm("Stop this run? What the agents have written so far is kept, but the run cannot be resumed.")) return;
    stopButton.disabled = true;
    const res = await fetch(`/api/runs/${encodeURIComponent(run.run_id)}?t=${encodeURIComponent(run.token)}`, { method: "DELETE" });
    stopButton.disabled = false;
    if (res.ok) {
      finished = true; if (source) source.close(); store.clear();
      stage("working", "failed"); stopButton.hidden = true; startButton.disabled = false;
      meta.textContent = "Run stopped after " + elapsed() + ".";
      say("Run stopped.");
    } else {
      say("The run could not be stopped (" + res.status + "). Try again.", true);
    }
  });

  // ---------- resume a run after a reload ----------
  const saved = store.load();
  if (saved && saved.run_id && saved.token && Date.now() - (saved.started || 0) < 6 * 3600 * 1000) {
    run = saved;
    startButton.disabled = true;
    say("Your run is still in progress.");
    begin(false);
  }
})();
