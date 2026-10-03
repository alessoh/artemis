// Content for "Artemis Phase 2 Runbook". Appended to guide_helpers.js at build time.
const Code = (lines) => new Paragraph({
  spacing: { before: 80, after: 200, line: 276 },
  shading: { fill: "EEF2F5", type: ShadingType.CLEAR, color: "auto" },
  border: { left: { style: BorderStyle.SINGLE, size: 12, color: TEAL, space: 8 } },
  indent: { left: 200, right: 200 },
  children: lines.flatMap((l, i) => [
    ...(i > 0 ? [new TextRun({ break: 1 })] : []),
    new TextRun({ text: l, font: "Consolas", size: 18, color: INK }),
  ]),
});
const Step = (n, title) => new Paragraph({
  heading: HeadingLevel.HEADING_2,
  children: [new TextRun(`Step ${n}. ${title}`)],
});

const children = [];

children.push(
  new Paragraph({ spacing: { before: 1400, after: 120 }, children: [new TextRun({ text: "ARTEMIS", font: HEAD_FONT, size: 22, bold: true, color: TEAL, characterSpacing: 120 })] }),
  new Paragraph({ spacing: { after: 200 }, children: [new TextRun({ text: "Phase 2 Runbook: The Real Lab", font: HEAD_FONT, size: 52, bold: true, color: INK })] }),
  new Paragraph({ spacing: { after: 600 }, children: [new TextRun({ text: "Earth-abundant solar absorbers, six agents, one measurable experiment", font: BODY_FONT, size: 28, italics: true, color: MUTED })] }),
  new Paragraph({
    border: { top: { style: BorderStyle.SINGLE, size: 6, color: NAVY, space: 8 } },
    spacing: { after: 80 }, children: [new TextRun({ text: "Repository: github.com/alessoh/artemis (commit d42ea38)", font: HEAD_FONT, size: 20, color: INK })],
  }),
  new Paragraph({ spacing: { after: 80 }, children: [new TextRun({ text: "Saturday, October 3, 2026", font: HEAD_FONT, size: 20, color: MUTED })] }),
  new Paragraph({ spacing: { before: 1000 }, children: runs("Phase 2 replaces the Phase 1 test agent with the real lab. The code is written, checked as far as my workspace allows, and pushed to your repository. One command on your computer builds the data, checks it, and starts the lab. This runbook explains what the lab does, what I could and could not test, and the steps you run.", { size: 21, color: MUTED }) }),
  new Paragraph({ children: [new PageBreak()] }),
);

children.push(
  H1("1. The question, turned into an experiment"),
  P("The flagship question is which earth-abundant, non-toxic crystals a lab should compute next to find excellent solar absorbers fastest. A question like that only becomes science when it can be scored, so the lab treats it as a search problem with an expensive measurement and a cheap one. The expensive measurement is SLME, the spectroscopic limited maximum efficiency that NIST JARVIS computes from a costly TBmBJ optical calculation. The cheap information is what any ordinary DFT relaxation gives: the OptB88vdW band gap, the formation energy, the energy above the convex hull, the composition and the crystal structure."),
  P("The lab's experiment sees only the cheap information and must put the candidate materials in the order it would spend expensive calculations on them. The frozen harness then reveals the hidden SLME values and counts how many expensive evaluations that order needed to find ten excellent, stable absorbers. Dividing what random search would need by what the lab's order needed gives the headline number, called acceleration. Random search scores 1.0, so an acceleration of 10 would mean the lab found the same discoveries with one tenth of the expensive computing."),
  P("Every definition was fixed before any ranking method was tried, and each is written into the harness so no agent can move the goalposts. The table lists them."),
  table([2600, 6760], ["Item", "Definition"], [
    ["Excellent absorber (a hit)", "SLME of at least 30 percent and energy above hull of at most 0.1 eV per atom"],
    ["Earth-abundant pool", "Every element at least 1 mg/kg in the Earth's crust (CRC Handbook, 97th edition), and no Cd, Hg, Pb, Tl, As or radioactive element"],
    ["Known, search and test sets", "The official JARVIS-Leaderboard SLME split: train is known to the lab, val is searched during the loop, test is scored once at the end"],
    ["Metric", "Acceleration: random search's expected evaluations to find ten hits, divided by the evaluations the lab's order needed"],
    ["Recommendations", "Earth-abundant materials in JARVIS that were never assessed for SLME, ranked by the lab's final method"],
  ]),
  Spacer(),
  P("I chose the 30 percent threshold after looking only at how many materials in each split exceed various SLME values, so that excellent absorbers are rare enough for search to matter. No ranking method was tuned before the definitions were fixed, and that choice is recorded in the decisions file in your repository."),
);

children.push(
  H1("2. The three files and the six agents"),
  P("The lab follows Karpathy's AutoResearch pattern. The harness, lab/solar/harness.py, is frozen: it checks the data fingerprint, builds the pool, runs each experiment under a five-minute limit, scores it, and writes every result to a ledger. The experiment, lab/solar/experiment.py, is the single function the agents improve; it starts as the textbook Shockley-Queisser rule that ranks materials by how close their band gap sits to 1.34 eV. The program, lab/solar/program.md, is your instruction to the agents, including the rule that they never stop to ask whether to continue until the experiment budget is spent."),
  P("The agents run together in one Omnigent session inside a Modal sandbox. The lead is the Compiler, which sets up the run, dispatches the specialists, keeps or discards each idea, and is the only agent allowed to run the final test. The table shows the team and the model each one uses, as you decided."),
  table([1800, 2200, 5360], ["Agent", "Model", "Job"], [
    ["Compiler (lead)", "Claude Opus 5.5", "Runs the loop, promotes approved ideas with a git commit, runs the final test once"],
    ["Scout", "Claude Haiku 4.5", "Quick literature searches (OpenAlex, then arXiv) and Materials Project cross-checks"],
    ["Planner", "Claude Opus 5.5", "Reads the ledger and proposes the next two or three testable ideas"],
    ["Experimenter", "Claude Opus 5.5", "Implements one idea as a trial file and evaluates it; several run in parallel"],
    ["Skeptic", "Claude Opus 5.5", "Reproduces any winning trial and checks it for leakage, overfitting and needless complexity"],
    ["Scribe", "Claude Opus 5.5", "Writes the final report from the ledger, the final test and the cross-checks"],
  ]),
  Spacer(),
  P("Three kinds of guardrail keep the run honest and affordable. Omnigent's own policies cap the lead's spending at 40 dollars and its tool calls at 900, block destructive shell commands and pushes, limit how many specialists start at once, and make the Scout, Planner and Skeptic read-only. The harness refuses any experiment whose code tries to read files, open network connections or reach around it, and it allows sixty experiments per run. Finally, every result carries the fingerprints of the harness and the data, so tampering would show."),
);

children.push(
  H1("3. What I tested, and what is still unproven"),
  P("I tested the harness end to end in my workspace: the data check, the pool, the scoring, the baselines, the ledger, the time limit (a runaway experiment is stopped), the refusal of experiments that try to read the data file, the check that every candidate appears exactly once, and the rule that the final test runs only once. The data builder downloaded the five pinned JARVIS-Leaderboard files from GitHub, matched every fingerprint, and produced a byte-identical snapshot when run twice. It also caught one material that the official split lists in both the training and the search set, which it now keeps in training only. The agent team was checked by Omnigent's own specification parser and validator, and every policy was confirmed to be one of Omnigent's registered built-ins and to accept its settings."),
  P("Four things remain unproven, and I want to be plain about them. First, my workspace cannot reach figshare, where JARVIS stores its full 2021 release, so the formulas and structures could only be exercised with stand-in values; the real snapshot is built on Modal when you run the command below, and its numbers have not yet been seen by anyone. Second, I have not watched the six agents run together live, because that needs your Anthropic key and Modal; Omnigent's code indicates that the specialists share the lead's sandbox and files, and the first run will confirm it. Third, Omnigent's spending cap only works if it knows the price of Claude Opus 5.5, which I could not confirm, so the sixty-experiment limit in the harness and a monthly limit in your Anthropic console are the dependable backstops. Fourth, the Materials Project and literature tools were tested only for their offline behavior, because my workspace cannot reach those services."),
);

children.push(
  H1("4. The steps you run"),
  P("Use the Anaconda PowerShell Prompt, as in Phase 1, and run every command from the artemis folder. Please do not press Ctrl+C in that window unless this runbook says it is safe, because it stops the running script."),
  Step(1, "Get the new code"),
  P("These commands bring your copy up to date and install the three science libraries the harness needs."),
  Code(["cd C:\\Users\\hales\\artemis", "git pull", "pip install -r requirements-solar.txt"]),
  Step(2, "Add your Materials Project key (optional)"),
  P("This lets the Scout check the lab's recommendations against the Materials Project. Sign in at next-gen.materialsproject.org, open your dashboard, and copy the API key shown there. Then run the command below and press Enter when it asks; it reads the key from your clipboard, saves it to your private .env file and to Modal, and never shows it on screen. If you skip this step the lab still runs, and the report says the cross-check was unavailable."),
  Code(["python scripts/make_secrets.py materials-project"]),
  Step(3, "Build the data, check it, and start the lab"),
  P("One command does the rest, explaining each step as it goes."),
  Code(["python scripts/run_phase2.py"]),
  P("First it builds the data snapshot on Modal, which takes a few minutes and downloads nothing large to your computer. Second it runs the harness on your computer and prints the pool sizes and the scores of three reference methods: random search, the plain Shockley-Queisser rule, and the same rule with stable materials first. These are the first real numbers of Phase 2, so please send me a screenshot of them. Third it uploads the snapshot to GitHub with git, because the lab's sandbox starts from a fresh copy of your repository. If git cannot upload from your computer, the script says so and names two files; attach those two files to our chat and I will add them for you, then you run the same command again."),
  P("Finally it starts the lab and shows its progress: the sandbox starting, the lead's short status lines after each wave of experiments, and the names of the tools the agents use. A full run can take one to several hours. The lab keeps running in the cloud even if you close the window, and here, unlike elsewhere, Ctrl+C is safe: it only stops the watching, not the lab. To reconnect later, run the watch command with the session number the script printed."),
  Code(["python scripts/run_phase2.py watch SESSION_ID"]),
  P("When the lab finishes, the script saves its report and full history in a new folder inside runs. If you ever need to end a run early and stop its sandbox, use the stop command; it saves what exists first."),
  Code(["python scripts/run_phase2.py stop SESSION_ID"]),
);

children.push(
  H1("5. What comes next"),
  P("When you send me the baseline screenshot, I will check the real numbers against the definitions, and if the snapshot reaches GitHub I will also run the harness myself and try a learned ranking method, so we know before the agents start what a good result looks like. After the first live run, I will read the ledger and the report with you, and we will decide whether the budgets and the hit definition should change; any change goes into the decisions file with your name on it. Phase 3 then builds the public website, with the lab's live progress, the ledger and the report shown in real time."),
);

children.push(
  H1("Sources"),
  source("JARVIS-Leaderboard, SLME benchmark files at commit 57afc55", "https://github.com/usnistgov/jarvis_leaderboard"),
  source("JARVIS-DFT 3D release 2021-08-18 (figshare)", "https://doi.org/10.6084/m9.figshare.6815699"),
  source("Choudhary et al., Accelerated discovery of efficient solar cell materials using quantum and machine-learning methods, Chem. Mater. 31, 5900 (2019)", "https://doi.org/10.1021/acs.chemmater.9b02166"),
  source("Abundance of elements in Earth's crust, CRC Handbook 97th edition values", "https://en.wikipedia.org/wiki/Abundance_of_elements_in_Earth%27s_crust"),
  source("Karpathy, autoresearch", "https://github.com/karpathy/autoresearch"),
  source("Omnigent", "https://github.com/omnigent-ai/omnigent"),
);

const doc = new Document({
  creator: "Claude",
  title: "Artemis Phase 2 Runbook",
  styles: {
    default: { document: { run: { font: BODY_FONT, size: 21, color: INK } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: HEAD_FONT, color: NAVY },
        paragraph: { spacing: { before: 420, after: 180 }, outlineLevel: 0, keepNext: true } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: HEAD_FONT, color: TEAL },
        paragraph: { spacing: { before: 260, after: 120 }, outlineLevel: 1, keepNext: true } },
    ],
  },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "Artemis  ·  Phase 2 Runbook", font: HEAD_FONT, size: 16, color: MUTED })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: HEAD_FONT, size: 16, color: MUTED })] })] }) },
    children,
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync("Artemis_Phase2_Runbook.docx", buf);
  console.log("written");
});
