/* Artemis shared behaviour: menu, on-page contents, and the strip chart. */
(() => {
  "use strict";

  // ---------- mobile menu ----------
  const toggle = document.querySelector(".menu-toggle");
  const nav = document.getElementById("site-nav");
  if (toggle && nav) {
    const label = toggle.querySelector(".menu-label");
    const setOpen = (open) => {
      toggle.setAttribute("aria-expanded", String(open));
      nav.dataset.open = String(open);
      document.body.classList.toggle("menu-open", open);
      if (label) label.textContent = open ? "Close" : "Menu";
    };
    toggle.addEventListener("click", () => setOpen(toggle.getAttribute("aria-expanded") !== "true"));
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") { setOpen(false); toggle.focus(); }
    });
    document.addEventListener("click", (e) => {
      if (toggle.getAttribute("aria-expanded") === "true" && !nav.contains(e.target) && !toggle.contains(e.target)) setOpen(false);
    });
  }

  // ---------- hero crystal: load Three.js only when the hero is on screen ----------
  const lattice = document.getElementById("lattice");
  if (lattice) {
    const load = () => {
      if (lattice.dataset.loading) return;
      lattice.dataset.loading = "1";
      const script = document.createElement("script");
      script.src = "/assets/lattice.js?v=" + (document.documentElement.dataset.version || "");
      document.body.appendChild(script);
    };
    const whenIdle = window.requestIdleCallback || ((fn) => setTimeout(fn, 200));
    if ("IntersectionObserver" in window) {
      const io = new IntersectionObserver((entries) => {
        if (entries.some((e) => e.isIntersecting)) { io.disconnect(); whenIdle(load); }
      });
      io.observe(lattice);
    } else { whenIdle(load); }
  }

  // ---------- data tables: label each cell so phones can show rows as cards ----------
  window.ArtemisStackTables = (root) => {
    (root || document).querySelectorAll("table.data:not(.status-table)").forEach((table) => {
      const heads = Array.from(table.querySelectorAll("thead th")).map((th) => th.textContent.trim());
      if (!heads.length) return;
      table.querySelectorAll("tbody tr").forEach((tr) => {
        Array.from(tr.children).forEach((td, i) => {
          if (heads[i]) td.setAttribute("data-label", heads[i]);
          // Keep mixed content (text, subscripts, overbars) together as one piece.
          if (i > 0 && td.childNodes.length > 1 && !td.querySelector(":scope > .cell")) {
            const wrap = document.createElement("span");
            wrap.className = "cell";
            while (td.firstChild) wrap.appendChild(td.firstChild);
            td.appendChild(wrap);
          }
        });
      });
      table.classList.add("stack");
      if (table.parentElement && table.parentElement.classList.contains("table-wrap")) table.parentElement.classList.add("stackable");
    });
  };
  window.ArtemisStackTables();

  // ---------- long tables on phones: show the kept rows first ----------
  document.querySelectorAll("[data-show-all]").forEach((button) => {
    const table = button.previousElementSibling && button.previousElementSibling.querySelector("table");
    if (!table) { button.hidden = true; return; }
    button.addEventListener("click", () => {
      const expanded = table.classList.toggle("expanded");
      button.textContent = expanded ? "Show only the kept trials" : "Show all 19 trials";
    });
  });

  // ---------- wide tables: drop the edge fade once scrolled to the end ----------
  document.querySelectorAll(".table-wrap").forEach((wrap) => {
    const update = () => wrap.classList.toggle("scrolled-end", wrap.scrollLeft + wrap.clientWidth >= wrap.scrollWidth - 4);
    wrap.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", update);
    update();
  });

  // ---------- on-page contents: highlight the section in view ----------
  const tocLinks = Array.from(document.querySelectorAll(".toc a[href^='#']"));
  if (tocLinks.length && "IntersectionObserver" in window) {
    const byId = new Map(tocLinks.map((a) => [a.getAttribute("href").slice(1), a]));
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        tocLinks.forEach((a) => a.classList.remove("active"));
        const link = byId.get(entry.target.id);
        if (link) link.classList.add("active");
      });
    }, { rootMargin: "-30% 0px -60% 0px" });
    byId.forEach((_, id) => { const el = document.getElementById(id); if (el) observer.observe(el); });
  }

  // ---------- strip chart (log scale, one row per method) ----------
  const SVG = "http://www.w3.org/2000/svg";
  const el = (name, attrs, text) => {
    const node = document.createElementNS(SVG, name);
    Object.entries(attrs || {}).forEach(([k, v]) => node.setAttribute(k, String(v)));
    if (text !== undefined) node.textContent = text;
    return node;
  };
  const fmt = (v) => (v >= 100 ? Math.round(v).toLocaleString("en-US") : (Math.round(v * 10) / 10).toString());

  function drawStrip(container, data) {
    const rows = data.rows;
    const width = Math.max(320, container.clientWidth);
    const narrow = width < 480;
    const labelW = narrow ? 0 : 128;
    const rowH = narrow ? 100 : 88;
    const top = 8, bottom = 44, right = 18, left = labelW + 4;
    const height = top + rows.length * rowH + bottom;
    const lo = Math.log10(8.6), hi = Math.log10(2600);
    const x = (v) => left + ((Math.log10(v) - lo) / (hi - lo)) * (width - left - right);

    const svg = el("svg", { class: "strip-chart", viewBox: `0 0 ${width} ${height}`, role: "img",
      "aria-label": data.title + ". " + rows.map((r) => `${r.label}: median ${fmt(r.median)}`).join("; ") });
    [10, 30, 100, 300, 1000].forEach((t) => {
      svg.appendChild(el("line", { class: "grid", x1: x(t), x2: x(t), y1: top, y2: top + rows.length * rowH }));
      svg.appendChild(el("text", { class: "axis-label", x: x(t), y: top + rows.length * rowH + 18, "text-anchor": "middle" }, t.toLocaleString("en-US")));
    });
    svg.appendChild(el("text", { class: "axis-label", x: width - right, y: height - 6, "text-anchor": "end" }, "calculations, log scale"));

    const tip = document.createElement("div");
    tip.className = "chart-tip"; tip.hidden = true;
    const show = (dot, text) => {
      const box = container.getBoundingClientRect();
      const d = dot.getBoundingClientRect();
      tip.textContent = text; tip.hidden = false;
      tip.style.left = (d.left - box.left + d.width / 2) + "px";
      tip.style.top = (d.top - box.top) + "px";
    };

    rows.forEach((row, i) => {
      const cy = top + i * rowH + rowH / 2 + (narrow ? 10 : 0);
      if (narrow) svg.appendChild(el("text", { class: "row-label", x: 0, y: cy - 30 }, row.label));
      else svg.appendChild(el("text", { class: "row-label", x: 0, y: cy + 5 }, row.label));
      const mx = x(row.median);
      const seen = new Map();
      row.values.forEach((v, j) => {
        // Equal values would hide each other, so stack repeats above and below the line.
        const key = Math.round(x(v) / 9);
        const k = seen.get(key) || 0;
        seen.set(key, k + 1);
        const jitter = (k % 2 ? 1 : -1) * Math.min(3, Math.ceil(k / 2)) * 5 + (k > 6 ? (k % 2 ? 2 : -2) : 0);
        const dot = el("circle", { class: "dot", cx: x(v), cy: cy + jitter, r: narrow ? 3.5 : 5, fill: row.color, tabindex: 0,
          "aria-label": `${row.label}, pool ${j + 1}: ${fmt(v)} calculations` });
        const text = `${row.label}, pool ${j + 1}: ${fmt(v)} calculations`;
        dot.addEventListener("mouseenter", () => show(dot, text));
        dot.addEventListener("focus", () => show(dot, text));
        dot.addEventListener("mouseleave", () => { tip.hidden = true; });
        dot.addEventListener("blur", () => { tip.hidden = true; });
        svg.appendChild(dot);
      });
      // Median on top of the dots, with a white outline so it reads over them.
      svg.appendChild(el("line", { x1: mx, x2: mx, y1: cy - 19, y2: cy + 19, stroke: "#ffffff", "stroke-width": 5, "stroke-linecap": "round" }));
      svg.appendChild(el("line", { class: "median", x1: mx, x2: mx, y1: cy - 19, y2: cy + 19 }));
      const labelText = "median " + fmt(row.median);
      if (narrow) {
        svg.appendChild(el("text", { class: "median-label", x: width - right, y: cy - 30, "text-anchor": "end" }, labelText));
      } else {
        const anchor = mx > width - 90 ? "end" : "middle";
        svg.appendChild(el("text", { class: "median-label", x: anchor === "end" ? mx + 4 : mx, y: cy - 30, "text-anchor": anchor }, labelText));
      }
    });
    container.replaceChildren(svg, tip);
  }

  document.querySelectorAll("[data-strip-chart]").forEach(async (container) => {
    try {
      const res = await fetch(container.dataset.src);
      if (!res.ok) throw new Error(String(res.status));
      const data = await res.json();
      drawStrip(container, data);
      let last = container.clientWidth;
      window.addEventListener("resize", () => {
        if (Math.abs(container.clientWidth - last) > 24) { last = container.clientWidth; drawStrip(container, data); }
      });
    } catch (err) {
      container.textContent = "The chart could not load. The table below has the same numbers.";
    }
  });
})();
