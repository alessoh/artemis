// Content for "Artemis Project 2: Runbook". Appended to guide_helpers.js at build time.
const children = [];
const Code = (text) => new Paragraph({
  spacing: { before: 60, after: 60 }, indent: { left: 360 },
  children: [new TextRun({ text, font: "Consolas", size: 19, color: INK })],
});

children.push(
  new Paragraph({ spacing: { before: 600, after: 120 }, children: [new TextRun({ text: "ARTEMIS  PROJECT 2", font: HEAD_FONT, size: 22, bold: true, color: TEAL, characterSpacing: 120 })] }),
  new Paragraph({ spacing: { after: 160 }, children: [new TextRun({ text: "Choosing UN-CCD's Alpha Without Labels: Runbook", font: HEAD_FONT, size: 38, bold: true, color: INK })] }),
  new Paragraph({ spacing: { after: 400 }, children: [new TextRun({ text: "What the lab will do, what has been checked, and how to launch it from your computer", font: BODY_FONT, size: 24, italics: true, color: MUTED })] }),
);

children.push(
  H1("What this program asks"),
  P("UN-CCD, the clustering method of Shi, Ceyhan and Billor, grows a ball around every data point until a statistical test at a significance level called alpha says the points inside no longer look randomly scattered. Everything the method finds depends on alpha. The paper sets it by hand for each dimension, 15 percent in two dimensions down to 0.1 percent in twenty, chosen by trial and error against the true answers, and its authors list automating that choice as future work. This program asks whether a rule that sees only the unlabelled data can choose alpha, and the direction of the ball search, as well as the paper's hand-tuned schedule. It is the fourth item of the authors' own future work and Project 2 of the review we wrote of their paper."),
  P("The lab follows the same pattern as the Langlands run. A team of AI agents writes and tests candidate rules in a single file, experiment.py, while a frozen harness that the agents cannot change scores every candidate on validation data with known answers. Every rule must decide from the data alone; the harness never lets it see a label. The agents also maintain a second file, formula.py, a rule that may look only at the number of points and the dimension and may contain at most three numeric constants, to test whether a simple closed-form expression captures most of the gain."),
);

children.push(
  H1("What has been built and checked"),
  P("UN-CCD itself was ported from the authors' R code to Python, line by line, keeping R's tie-breaking so that the two give the same answer. On 60 test cases, the six real datasets of the paper's Table 13 at two settings each and 48 simulated datasets in two to twenty dimensions, the port produced exactly the same ball radii, the same dominating balls and the same clusters as the authors' code, and it runs three to ten times faster. The Monte Carlo reference tables the method needs were rebuilt for 23 significance levels in ten dimensions with the generator we validated against the authors' own in Project 1."),
  P("The data follow the paper's simulation design exactly: uniform and Gaussian clusters at the paper's centres, in 2, 3, 5, 10 and 20 dimensions, with two, three or five clusters and, in a few regimes, background noise. A development split of 32 datasets is free for the agents to explore; a validation split of 64 datasets is where every candidate is scored, under a budget of 40 evaluations. Every clustering the validation data can produce, at all 15 permitted values of alpha in both search directions, was computed in advance, so an evaluation takes seconds and the agents' budget goes on ideas rather than computing."),
  P("The final test is sealed. It consists of 45 regimes the paper never ran, in 4, 7 and 15 dimensions, with 30, 300 or 700 points, two, four or six clusters, up to 30 percent noise and new cluster layouts, two datasets each, together with five real benchmark datasets the paper did not use (aggregation, compound, jain, glass and yeast). The synthetic test data are drawn from a secret random seed whose fingerprint is published in the program, so the agents cannot tune to them. I have already generated them on this machine and started computing their clusterings, which takes several hours, but they are kept out of the repository and the sandbox, and no rule is scored on them until the lab has frozen its final files. After the run I check that those files match the fingerprints the lab recorded and run the test once."),
  P("An independent review of the harness before launch found eleven issues, among them a final test that did not yet confirm it was scoring the frozen files, a formula rule that could hide extra constants in arithmetic or strings, and output from a rule that could disturb the harness; all were fixed and retested. A check also confirmed that a rule which tries to open the data files is blocked at run time."),
);

children.push(
  H1("What the baselines already show"),
  P("Before any agent has run, the validation data give a striking first result. The simplest label-free rule, which tries every alpha and keeps the one whose clustering has the best silhouette score, already beats the paper's hand-tuned schedule. This is the lab's starting rule. The ceilings in the table below choose the best alpha for each dataset using the true labels, which no real rule can do, and show how much room is left."),
  table(
    [4300, 2400, 2660],
    ["Rule (validation split, 64 datasets)", "Mean ARI", "95% interval"],
    [
      ["Paper's hand-tuned schedule", "0.906", "0.862 to 0.944"],
      ["Fixed alpha of 1% (the paper's stated real-data setting)", "0.823", "0.757 to 0.882"],
      ["Fixed alpha of 5%", "0.860", "0.804 to 0.906"],
      ["Best silhouette (label-free; the starting rule)", "0.941", "0.899 to 0.975"],
      ["Ceiling: best alpha per dataset, ascending search", "0.965", "0.943 to 0.983"],
      ["Ceiling: best alpha and search direction per dataset", "0.968", "0.946 to 0.986"],
    ],
  ),
  Caption("Table 1. Baselines on the validation split. ARI is the adjusted Rand index, 1 for a perfect clustering; noise points are left out of it. Intervals are bootstrap intervals over regimes."),
  P("So the agents start from a rule that is already ahead of the paper on the paper's own kind of data, and their task is to close as much as possible of the remaining gap to the ceiling, and to find a simple formula. Whether any of this carries over to new kinds of data is what the sealed test decides, through two hypotheses fixed in advance. H1 says the lab's final rule matches the paper's schedule on the held-out regimes, meaning the lower end of the 95 percent interval of the difference stays above minus 0.02. H2 says the lab's formula matches the lab's final rule in the same sense."),
);

children.push(
  H1("How to launch the run"),
  P("The run needs your Omnigent server and keys, exactly as the Langlands run did, so it starts from your computer. Open a terminal in your artemis folder and run these commands. The first two bring in the new branch; the third installs the three Python packages the lab uses, which you may already have; the last checks the harness on your computer and, if all is well, starts the lab in a Modal sandbox and streams its progress."),
  Code("git fetch origin"),
  Code("git checkout unccd-alpha-lab"),
  Code("pip install -r requirements-unccd-alpha.txt"),
  Code("python scripts/run_unccd_alpha.py"),
  P("The check step prints the harness fingerprints, the list of datasets, the baselines on the development split and one free trial of the starting rule, and takes about a minute. The launch step then creates the session and shows the lead agent's messages as they arrive. The lab keeps running in the cloud if you close the window; to reconnect, run the same script with the word watch and the session number it printed. If anything stops with a message beginning STOPPED, send me a screenshot; no secret is ever printed."),
  P("The run uses the same team and the same limits as the Langlands run: Claude Opus 5.5 for the lead, the Planner, the Experimenters, the Skeptic and the Scribe, Claude Haiku 4.5 for the Scout's literature searches, a spending limit of 60 dollars and a cap of 700 tool calls. Because evaluations take seconds, the run should take a few hours at most, and its cost is set mainly by how much the agents think and write. If you would rather use other models, the model names are on one line in each file under lab/agents/unccd_alpha_lab, and I can change them before you launch."),
);

children.push(
  H1("When the run finishes"),
  P("The lab ends by freezing its final rule and formula, recording their fingerprints, and writing a report of what it tried and what it learned on the validation data. The launch script saves the report and the full record of every agent's messages in the runs folder on your computer. Keep that folder private, as before, because the records can include keys visible inside the sandbox."),
  P("Then send me the report, or tell me the session number. I will rebuild the final files from the lab's last message, confirm that their fingerprints match the frozen record, and run the final test once on the sealed data, whose clusterings will by then be computed. You will get a report with the verdicts on H1 and H2, every rule's score on the held-out regimes and on the five real datasets, and an independent check of the numbers, as for Project 1."),
);

children.push(
  H1("Where everything is"),
  P("Everything is on the branch unccd-alpha-lab of github.com/alessoh/artemis. The program, the frozen harness and the Python port are in lab/unccd_alpha, with program.md as the instructions the agents follow; the agents' instructions are in lab/agents/unccd_alpha_lab; the launch script is scripts/run_unccd_alpha.py. The port's validation record is lab/unccd_alpha/data/port_validation.json, and the R script and comparison that produced it are in lab/unccd_alpha/validation. The secret test seed is not in the repository; only its SHA-256 fingerprint is, in program.md."),
);

const doc = new Document({
  creator: "H. P. Alesso", title: "Artemis Project 2: Runbook",
  styles: {
    default: { document: { run: { font: BODY_FONT, size: 22, color: INK } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: HEAD_FONT, color: NAVY },
        paragraph: { spacing: { before: 360, after: 160 }, outlineLevel: 0, keepNext: true } },
    ],
  },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: HEAD_FONT, size: 16, color: MUTED })] })] }) },
    children,
  }],
});
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync("../Artemis_UNCCD_Project2_Runbook.docx", buf); console.log("written"); });
