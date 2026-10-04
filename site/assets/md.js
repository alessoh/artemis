/* A small, safe markdown renderer for saved lab reports.
   All text is HTML-escaped first; only a fixed set of markdown constructs
   become tags, and links are limited to http(s), mailto and site-relative URLs. */
(() => {
  "use strict";
  const escape = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

  function safeUrl(url) {
    const u = url.trim();
    if (/^(https?:|mailto:)/i.test(u) || u.startsWith("/") || u.startsWith("#")) return u;
    return null;
  }

  function inline(text) {
    // text is already escaped
    const codes = [];
    let out = text.replace(/`([^`]+)`/g, (_, c) => { codes.push(c); return `\u0000${codes.length - 1}\u0000`; });
    out = out.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (m, label, url) => {
      const href = safeUrl(url.replace(/&amp;/g, "&"));
      return href ? `<a href="${escape(href)}" rel="nofollow noopener">${label}</a>` : label;
    });
    out = out.replace(/(^|[\s(])(https?:\/\/[^\s<)]+)/g, (m, pre, url) => `${pre}<a href="${url}" rel="nofollow noopener">${url}</a>`);
    out = out.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    out = out.replace(/(^|[^*\w])\*([^*\n]+)\*(?!\w)/g, "$1<em>$2</em>");
    out = out.replace(/\u0000(\d+)\u0000/g, (_, i) => `<code>${codes[Number(i)]}</code>`);
    return out;
  }

  function splitRow(line) {
    return line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((c) => c.trim());
  }

  function render(markdown) {
    const lines = escape(markdown.replace(/\r/g, "")).split("\n");
    const html = [];
    let i = 0;
    while (i < lines.length) {
      const line = lines[i];
      if (/^```/.test(line)) {
        const body = [];
        i += 1;
        while (i < lines.length && !/^```/.test(lines[i])) { body.push(lines[i]); i += 1; }
        i += 1;
        html.push(`<pre><code>${body.join("\n")}</code></pre>`);
        continue;
      }
      const heading = line.match(/^(#{1,4})\s+(.+)$/);
      if (heading) {
        const level = Math.min(4, heading[1].length + 1);
        html.push(`<h${level}>${inline(heading[2])}</h${level}>`);
        i += 1; continue;
      }
      if (/^\s*(---|\*\*\*)\s*$/.test(line)) { html.push("<hr>"); i += 1; continue; }
      if (/^\s*\|/.test(line) && i + 1 < lines.length && /^\s*\|?\s*:?-{3,}/.test(lines[i + 1])) {
        const head = splitRow(line);
        i += 2;
        const rows = [];
        while (i < lines.length && /^\s*\|/.test(lines[i])) { rows.push(splitRow(lines[i])); i += 1; }
        html.push('<div class="table-wrap"><table class="data"><thead><tr>' + head.map((h) => `<th>${inline(h)}</th>`).join("") +
          "</tr></thead><tbody>" + rows.map((r) => "<tr>" + r.map((c) => `<td>${inline(c)}</td>`).join("") + "</tr>").join("") + "</tbody></table></div>");
        continue;
      }
      if (/^\s*([-*]|\d+\.)\s+/.test(line)) {
        const ordered = /^\s*\d+\./.test(line);
        const items = [];
        while (i < lines.length && /^\s*([-*]|\d+\.)\s+/.test(lines[i])) {
          let item = lines[i].replace(/^\s*([-*]|\d+\.)\s+/, "");
          i += 1;
          while (i < lines.length && /^\s{2,}\S/.test(lines[i]) && !/^\s*([-*]|\d+\.)\s+/.test(lines[i])) { item += " " + lines[i].trim(); i += 1; }
          items.push(`<li>${inline(item)}</li>`);
        }
        html.push(ordered ? `<ol>${items.join("")}</ol>` : `<ul>${items.join("")}</ul>`);
        continue;
      }
      if (/^&gt;\s?/.test(line)) {
        const quote = [];
        while (i < lines.length && /^&gt;\s?/.test(lines[i])) { quote.push(lines[i].replace(/^&gt;\s?/, "")); i += 1; }
        html.push(`<blockquote><p>${inline(quote.join(" "))}</p></blockquote>`);
        continue;
      }
      if (!line.trim()) { i += 1; continue; }
      const para = [line];
      i += 1;
      while (i < lines.length && lines[i].trim() && !/^(#{1,4}\s|```|\s*\||\s*([-*]|\d+\.)\s+|&gt;)/.test(lines[i])) { para.push(lines[i]); i += 1; }
      html.push(`<p>${inline(para.join(" "))}</p>`);
    }
    return html.join("\n");
  }

  window.ArtemisMarkdown = { render, escape };
})();
