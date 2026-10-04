/* System status page: live checks of each part of the lab. */
(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const table = $("hops");
  if (!table) return;
  const set = (hop, label, kind) => {
    const tag = table.querySelector(`[data-hop="${hop}"] [data-state]`);
    if (!tag) return;
    tag.textContent = label;
    tag.className = "tag " + ({ ok: "tag-good", wait: "tag-run", bad: "tag-bad", off: "" }[kind] || "");
  };
  const say = (msg, bad) => { const s = $("check-status"); s.textContent = msg; s.className = "form-status" + (bad ? " bad" : ""); };

  fetch("/api/status", { cache: "no-store" }).then((r) => r.json().then((b) => [r.ok, b])).then(([ok, b]) => {
    set("website", ok ? "working" : "error", ok ? "ok" : "bad");
    if (!b.configured) set("server", "not configured", "bad");
    else if (b.server_ok && b.credentials_ok) set("server", "working", "ok");
    else set("server", b.server_ok ? "login refused" : "not reachable", "bad");
    if (b.database === "connected") set("database", "working", "ok");
    else if (b.database === "not configured") set("database", "not configured", "off");
    else set("database", "error", "bad");
  }).catch(() => { set("website", "not reachable", "bad"); set("server", "unknown", "off"); set("database", "unknown", "off"); });

  const EVENTS = ["artemis.relay", "session.sandbox_status", "turn.started", "turn.completed", "turn.failed",
    "response.output_text.delta", "response.completed", "response.failed", "response.error"];
  let source = null;
  $("check-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const code = $("check-code").value.trim();
    if (!code) { say("Enter the access code to run the check.", true); return; }
    if (source) source.close();
    $("check-button").disabled = true;
    ["sandbox", "model", "stream"].forEach((h) => set(h, "waiting", "wait"));
    say("Creating a test session.");
    try {
      const res = await fetch("/api/sessions", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ access_code: code }) });
      const s = await res.json().catch(() => ({}));
      if (!res.ok) { say(typeof s.detail === "string" ? s.detail : "The check could not start (" + res.status + ").", true); $("check-button").disabled = false; ["sandbox", "model", "stream"].forEach((h) => set(h, "not tested", "off")); return; }
      const q = `?t=${encodeURIComponent(s.stream_token)}`;
      const reply = $("check-text");
      reply.textContent = ""; $("check-reply").hidden = false;
      let done = false;
      source = new EventSource(`/api/sessions/${encodeURIComponent(s.session_id)}/stream${q}`);
      const handle = (m) => {
        let ev; try { ev = JSON.parse(m.data); } catch (_) { return; }
        if (ev.type === "artemis.relay" && ev.state === "connected") set("stream", "connected", "wait");
        else if (ev.type === "session.sandbox_status") set("sandbox", ev.stage === "ready" ? "working" : ev.stage, ev.stage === "failed" ? "bad" : ev.stage === "ready" ? "ok" : "wait");
        else if (ev.type === "response.output_text.delta") { set("sandbox", "working", "ok"); set("model", "working", "ok"); set("stream", "working", "ok"); reply.textContent += ev.delta || ""; }
        else if ((ev.type === "turn.completed" || ev.type === "response.completed") && !done) {
          done = true; say("Every part of the lab answered. The system is working end to end.");
          source.close();
          fetch(`/api/sessions/${encodeURIComponent(s.session_id)}${q}`, { method: "DELETE" });
          $("check-button").disabled = false;
        } else if (ev.type === "turn.failed" || ev.type === "response.failed" || ev.type === "response.error") { set("model", "error", "bad"); say("The test agent reported an error.", true); }
      };
      source.onmessage = handle;
      EVENTS.forEach((n) => source.addEventListener(n, handle));
      const sent = await fetch(`/api/sessions/${encodeURIComponent(s.session_id)}/message${q}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ message: $("check-message").value }) });
      if (!sent.ok) { say("The question could not be delivered (" + sent.status + ").", true); $("check-button").disabled = false; }
      else if (!done) say("Question delivered. Waiting for the reply.");
    } catch (err) { say("The check could not reach the website backend.", true); $("check-button").disabled = false; }
  });
})();
