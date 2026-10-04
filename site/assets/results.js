/* Results list and single saved-run page. */
(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const STATUS = {
    complete: ["Complete", "tag-good"], running: ["In progress", "tag-run"], starting: ["Starting", "tag-run"],
    failed: ["Ended without a report", "tag-bad"], stopped: ["Stopped", "tag-warn"],
  };
  const KIND = { solar: "Flagship program", proposal: "Experiment proposal" };
  const dateLabel = (iso) => (iso ? new Date(iso).toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" }) : "");
  const text = (tag, value, cls) => { const n = document.createElement(tag); n.textContent = value; if (cls) n.className = cls; return n; };

  function metaRow(run) {
    const meta = document.createElement("div");
    meta.className = "result-meta";
    const [label, cls] = STATUS[run.status] || [run.status, ""];
    meta.append(text("span", label, "tag " + cls), text("span", KIND[run.kind] || run.kind));
    const time = text("time", dateLabel(run.completed_at || run.created_at));
    time.dateTime = run.completed_at || run.created_at || "";
    meta.append(text("span", ""));
    meta.lastChild.appendChild(time);
    if (run.detail) meta.append(text("span", run.detail));
    return meta;
  }

  // ---------- list ----------
  const list = $("result-list");
  if (list) {
    const status = $("results-status");
    fetch("/api/results", { cache: "no-store" }).then((r) => r.json()).then((body) => {
      const runs = (body.runs || []);
      if (!body.database) { status.textContent = "Runs started from the Lab page appear here once the results database is connected."; return; }
      if (!runs.length) { status.innerHTML = 'No runs from the Lab page yet. <a href="/lab">Start an investigation</a> and it will appear here.'; return; }
      runs.forEach((run) => {
        const li = document.createElement("li");
        const main = document.createElement("div");
        const h = document.createElement("h3");
        const a = text("a", run.title || "Lab run");
        a.href = "/results/run?id=" + encodeURIComponent(run.id);
        h.appendChild(a);
        main.append(h);
        if (run.question && run.kind === "proposal") main.append(text("p", run.question.length > 220 ? run.question.slice(0, 217) + "..." : run.question));
        main.append(metaRow(run));
        const side = document.createElement("div");
        side.className = "side chev";
        side.setAttribute("aria-hidden", "true");
        side.textContent = "\u203A";
        li.append(main, side);
        list.appendChild(li);
      });
    }).catch(() => { status.textContent = "Saved runs could not be loaded right now. The published results above are always available."; });
  }

  // ---------- one run ----------
  const body = $("run-body");
  if (body) {
    const id = new URLSearchParams(location.search).get("id") || "";
    const fail = (msg) => {
      $("run-title").textContent = "Run not found";
      const actions = document.createElement("div");
      actions.className = "actions";
      const home = text("a", "See all results", "button button-primary"); home.href = "/results";
      const lab = text("a", "Start an investigation", "button button-quiet"); lab.href = "/lab";
      actions.append(home, lab);
      body.replaceChildren(text("p", msg, "lede"), actions);
    };
    if (!/^[A-Za-z0-9_\-]{4,128}$/.test(id)) { fail("This link does not name a saved run. Choose one from the Results page."); }
    else {
      fetch("/api/results/" + encodeURIComponent(id), { cache: "no-store" }).then(async (r) => {
        if (r.status === 404) return fail("No saved run has this id. It may have been started without the results database.");
        if (!r.ok) return fail("The saved run could not be loaded right now. Please try again in a minute.");
        const run = await r.json();
        document.title = (run.title || "Lab run") + " | Artemis";
        // Non-breaking hyphens keep words such as "metal-organic" on one line.
        $("run-title").textContent = (run.title || "Lab run").replace(/(\w)-(\w)/g, "$1\u2011$2");
        $("run-meta").replaceWith(metaRow(run));
        const parts = [];
        if (run.question) {
          const q = document.createElement("div");
          q.className = "callout";
          q.style.marginBottom = "28px";
          q.append(text("strong", "Question: "), document.createTextNode(run.question));
          parts.push(q);
        }
        const prose = document.createElement("div");
        prose.className = "prose";
        if (run.report_md) {
          // The page title already shows the report's first heading.
          const md = run.report_md.replace(/^\s*#\s+.+\n/, "");
          prose.innerHTML = window.ArtemisMarkdown.render(md);
          if (window.ArtemisStackTables) window.ArtemisStackTables(prose);
          parts.push(prose);
        } else {
          parts.push(text("p", run.status === "running" || run.status === "starting"
            ? "This run is still in progress. Its report appears here when it finishes; the lead agent's latest messages are below."
            : "This run ended without a final report. The lead agent's messages are below.", "lede"));
        }
        const messages = Array.isArray(run.messages) ? run.messages : [];
        if (messages.length) {
          const details = document.createElement("details");
          details.className = "report";
          details.style.marginTop = "28px";
          if (!run.report_md) details.open = true;
          details.appendChild(text("summary", `The lead agent's messages (${messages.length})`));
          const inner = document.createElement("div");
          inner.className = "feed";
          inner.style.maxHeight = "none";
          messages.forEach((m) => {
            const art = document.createElement("article");
            art.appendChild(text("div", m.replace(/ARTEMIS-RUN-COMPLETE\s*$/m, ""), "msg"));
            inner.appendChild(art);
          });
          details.appendChild(inner);
          parts.push(details);
        }
        body.replaceChildren(...parts);
      }).catch(() => fail("The saved run could not be loaded right now. Please try again in a minute."));
    }
  }
})();
