// Build "Artemis Architecture Discussion Paper No. 1" as a Word document.
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, ImageRun,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle, Header, Footer,
  PageNumber, PageBreak, ExternalHyperlink, TabStopType,
} = require("docx");

const NAVY = "1F3A5F";
const INK = "14213D";
const MUTED = "5B6577";
const TEAL = "0F766E";
const BODY_FONT = "Georgia";
const HEAD_FONT = "Arial";

// ---------- helpers ----------
function runs(text, base = {}) {
  // Supports **bold** and *italic* inline markers.
  const out = [];
  const re = /(\*\*[^*]+\*\*|\*[^*]+\*)/g;
  let last = 0, m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), ...base }));
    const t = m[0];
    if (t.startsWith("**")) out.push(new TextRun({ text: t.slice(2, -2), bold: true, ...base }));
    else out.push(new TextRun({ text: t.slice(1, -1), italics: true, ...base }));
    last = m.index + t.length;
  }
  if (last < text.length) out.push(new TextRun({ text: text.slice(last), ...base }));
  return out;
}
const P = (text, opts = {}) => new Paragraph({ children: runs(text), spacing: { after: 160, line: 312 }, ...opts });
const H1 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(text)] });
const H2 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(text)] });
const Caption = (text) => new Paragraph({
  alignment: AlignmentType.LEFT, spacing: { before: 80, after: 280 },
  children: runs(text, { size: 18, color: MUTED, font: HEAD_FONT }),
});
const Img = (file, w, h) => new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { before: 200, after: 60 },
  children: [new ImageRun({ type: "png", data: fs.readFileSync(file), transformation: { width: w, height: h } })],
});
const Pull = (text) => new Paragraph({
  spacing: { before: 200, after: 240, line: 320 }, indent: { left: 540, right: 540 },
  border: { left: { style: BorderStyle.SINGLE, size: 18, color: TEAL, space: 12 } },
  children: runs(text, { italics: true, color: INK, size: 23 }),
});

const border = { style: BorderStyle.SINGLE, size: 4, color: "C9CFD8" };
const borders = { top: border, bottom: border, left: border, right: border };
function table(colWidths, header, rows) {
  const total = colWidths.reduce((a, b) => a + b, 0);
  const cell = (text, w, isHead) => new TableCell({
    borders, width: { size: w, type: WidthType.DXA },
    shading: isHead ? { fill: "E8EEF6", type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: { top: 90, bottom: 90, left: 110, right: 110 },
    children: [new Paragraph({
      spacing: { after: 0, line: 264 },
      children: runs(text, { size: 17, font: HEAD_FONT, bold: isHead, color: isHead ? NAVY : INK }),
    })],
  });
  return new Table({
    width: { size: total, type: WidthType.DXA }, columnWidths: colWidths,
    rows: [
      new TableRow({ tableHeader: true, children: header.map((h, i) => cell(h, colWidths[i], true)) }),
      ...rows.map((r) => new TableRow({ cantSplit: true, children: r.map((c, i) => cell(c, colWidths[i], false)) })),
    ],
  });
}
const Spacer = () => new Paragraph({ spacing: { after: 120 }, children: [] });

function source(label, url) {
  return new Paragraph({
    spacing: { after: 100, line: 276 }, indent: { left: 360, hanging: 360 },
    children: [
      new TextRun({ text: label + ". ", size: 19 }),
      new ExternalHyperlink({ link: url, children: [new TextRun({ text: url, style: "Hyperlink", size: 19 })] }),
    ],
  });
}

