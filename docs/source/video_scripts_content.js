// Content for "Artemis Video Scripts". Appended to guide_helpers.js at build time.
const children = [];
const S = (t) => new Paragraph({ children: runs(t, { size: 24 }), spacing: { after: 220, line: 360 } });
children.push(
  new Paragraph({ spacing: { after: 120 }, children: [new TextRun({ text: "ARTEMIS", font: HEAD_FONT, size: 22, bold: true, color: TEAL, characterSpacing: 120 })] }),
  new Paragraph({ spacing: { after: 360 }, children: [new TextRun({ text: "Hackathon Video Scripts", font: HEAD_FONT, size: 44, bold: true, color: INK })] }),
  H1("Product demo (about 60 seconds, 146 words)"),
  S("Hi, I'm Peter Alesso, and this is Artemis, an autonomous AI lab that turns a scientific question into a measured experiment and shows all of its work. It combines Elon Musk's first-principles thinking with Andrej Karpathy's AutoResearch loop, where AI agents run many small experiments against a judge they cannot change."),
  S("Our first run asked which earth-abundant crystals scientists should calculate next to find excellent solar-cell materials. Six agents worked for three hours without human help. On data they had never seen, their method found every excellent candidate in 8 expensive calculations. The textbook rule needed 20, and random picking about 344."),
  S("The full report is published, including what failed, and fifteen materials to compute next."),
  S("On the Lab page, anyone can ask a question and watch the agents draft a testable experiment live. Every run is saved and published."),
  S("Artemis. Faster science that stays honest."),
  new Paragraph({ children: [new PageBreak()] }),
  H1("Technical walkthrough (about 60 seconds, 144 words)"),
  S("Artemis is built on two ideas. The first is Elon Musk's algorithm: question every requirement, delete, simplify, accelerate, and only then automate. Here, the expensive step is the calculation, so the lab only decides which calculation to run next."),
  S("The second is Andrej Karpathy's AutoResearch, with three files. Harness dot py is frozen and fingerprinted, holding the NIST JARVIS data, the threshold and the metric. Experiment dot py is the one file the agents may change. Program dot md holds the human's instructions."),
  S("The agents run in Omnigent, the open-source harness from Databricks, in Modal sandboxes. A Compiler leads, a Scout on Claude Haiku 4.5 searches the literature, and a Planner, Experimenters, a Skeptic and a Scribe run on Claude Opus 5.5. The Skeptic re-runs every gain, and the held-out test runs once."),
  S("Vercel streams each run live, and Neon Postgres saves every report."),
);
const doc = new Document({
  creator: "Claude", title: "Artemis Hackathon Video Scripts",
  styles: {
    default: { document: { run: { font: BODY_FONT, size: 21, color: INK } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: HEAD_FONT, color: NAVY },
        paragraph: { spacing: { before: 240, after: 240 }, outlineLevel: 0, keepNext: true } },
    ],
  },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    children,
  }],
});
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync("Artemis_Video_Scripts.docx", buf); console.log("written"); });
