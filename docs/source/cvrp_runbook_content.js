// Content for "Artemis Routing Program Runbook". Appended to guide_helpers.js at build time.
const children = [];
const Cmd = (t) => new Paragraph({ spacing: { after: 80 }, indent: { left: 540 },
  children: [new TextRun({ text: t, font: "Consolas", size: 20, color: INK })] });

children.push(
  new Paragraph({ spacing: { before: 1400, after: 120 }, children: [new TextRun({ text: "ARTEMIS", font: HEAD_FONT, size: 22, bold: true, color: TEAL, characterSpacing: 120 })] }),
  new Paragraph({ spacing: { after: 200 }, children: [new TextRun({ text: "The Routing Program", font: HEAD_FONT, size: 52, bold: true, color: INK })] }),
  new Paragraph({ spacing: { after: 600 }, children: [new TextRun({ text: "Vehicle routing on the CVRPLIB benchmark: what was built, what it can and cannot claim, and how to run it", font: BODY_FONT, size: 28, italics: true, color: MUTED })] }),
  new Paragraph({ border: { top: { style: BorderStyle.SINGLE, size: 6, color: NAVY, space: 8 } }, spacing: { after: 80 },
    children: [new TextRun({ text: "Branch cvrp-lab of github.com/alessoh/artemis", font: HEAD_FONT, size: 20, color: INK })] }),
  new Paragraph({ spacing: { after: 80 }, children: [new TextRun({ text: "Wednesday, October 7, 2026", font: HEAD_FONT, size: 20, color: MUTED })] }),
  new Paragraph({ spacing: { before: 1000 }, children: runs("You asked Artemis to take on vehicle routing on the public CVRPLIB benchmark, on a new GitHub branch. This document explains the program I built for the lab, the checks it passed before any agent touches it, the honest odds of a record, and the four commands that start the run from your computer.", { size: 21, color: MUTED }) }),
  new Paragraph({ children: [new PageBreak()] }),
);

children.push(
  H1("1. The question"),
  P("A delivery company sends trucks of fixed capacity from one depot to serve every customer exactly once, and wants the shortest total distance. This is the capacitated vehicle routing problem. The CVRPLIB X benchmark, published by Uchoa and colleagues in 2017, holds 100 such problems with 100 to 1,000 customers, and the research community keeps a table of the best route sets ever found for each one."),
  P("The lab gets a precise, measurable question. With the same short time limit on one processor core, three seconds for every hundred customers, can the agents build a solver that comes closer to those best-known solutions than PyVRP, a state-of-the-art open-source routing library, run with its default settings? The score is the average percentage by which a solver's routes are longer than the best known, so lower is better and zero would mean matching the record on every problem."),
  P("A record is a separate and much harder goal. After the lab finishes, its final solver can be given an hour or more on the largest problems, and any route set shorter than the published best would be a new record that anyone can verify in seconds."),
);

children.push(
  H1("2. What a record would take, honestly"),
  P("I want to set expectations plainly. The X benchmark has been attacked for nearly a decade by the strongest groups in the field, using far more computing than this lab will spend, and many of the smaller problems are already proven optimal, which means no shorter answer exists. The best-known solutions on the larger problems are the product of long runs of world-class algorithms. A new record from an afternoon of agent research plus a few hours of computing is possible only on the largest problems and is unlikely even there."),
  P("The realistic and still worthwhile result is the fixed-time comparison. Before any agent starts, PyVRP's default settings average 1.23 to 1.30 percent above the best-known solutions on the eight practice problems, and the textbook savings method averages 6.85 percent. If the agents produce a solver that holds a clear gain over PyVRP on seventeen problems they never saw, under rules fixed in advance, that is a real and checkable result, and it is exactly the kind of evidence the Artemis method is built to produce."),
);

children.push(
  H1("3. How the program is built"),
  P("The program follows the same three-file AutoResearch pattern as the solar run. The frozen judge, harness.py, checks every answer itself: each customer visited exactly once, no truck over capacity, and the length computed with the community's convention of rounding every distance to the nearest whole number. The agents may change only experiment.py, which starts as an exact copy of PyVRP's default solver. The instructions, program.md, fix the rules before the first experiment."),
  P("The data come from the PyVRP project's public mirror of CVRPLIB, pinned to one version from August 2026. When I built the snapshot, the harness re-computed the published cost of all 100 best-known solutions from their routes and matched every one exactly, which is the test that the judge measures distance the way the rest of the field does. The snapshot keeps only those costs, not the routes, so no experiment can copy a published answer."),
  table([2300, 1500, 5560], ["Split", "Problems", "Use"], [
    ["Train", "52", "Free practice, any number of runs"],
    ["Practice (val)", "8", "The loop's score; 60 evaluations and 20 rechecks per run"],
    ["Test", "17", "Held out, scored once at the end"],
    ["Scale", "8", "Held out larger problems, scored once, to see if gains carry over"],
    ["Hunt", "15", "Larger problems open for record attempts"],
  ]),
  Caption("The pre-registered splits. Problems under 600 customers form the loop; 600 and above are scale and hunt."),
  P("Because the solvers stop on wall-clock time, the same code can score slightly differently from run to run. I measured that noise before writing the rules: identical PyVRP runs varied by a standard deviation of 0.085 percentage points. The program therefore keeps a new idea only if it beats the current best by at least 0.15 points on the first run and by at least 0.10 points on two fresh runs that the Skeptic performs."),
);

children.push(
  H1("4. The checks it passed"),
  P("I asked a separate reviewer, who had not seen the code being written, to try to break the judge. It found seven serious holes in my first version and demonstrated each one. A solver could reach into the judge's own memory, rewrite the experiment log, run past its time limit by fooling the clock it was timed with, start hidden extra processes to use more than one core, and hide forbidden code from the checker. Its best cheat improved the score from 0.56 to 0.41 percent without being a better solver."),
  P("I rebuilt the parts responsible. Each solver now runs in a separate, clean process that the judge times from outside, one at a time, with one numerical thread, and the judge kills the whole process group after every run. The code checker now works from an allowlist of permitted modules and refuses anything that opens files, inspects the interpreter or carries large tables of numbers. Every evaluation is logged before it starts, so an interrupted run still counts against the budget, and the final test can be started only once and only on the promoted solver. I then re-ran every one of the reviewer's attacks: each is now refused or stopped, while the honest copy of PyVRP still scores normally."),
  P("Finally I ran the whole pipeline end to end on this workspace, the baselines, an evaluation, a recheck and the final test on the held-out problems, to make sure the lab will not stumble over the harness itself. On the seventeen test problems PyVRP's default scored 0.92 percent above the best known and the savings method 4.82 percent; on the eight larger scale problems they scored 1.74 and 4.96 percent. An earlier pipeline run gave 0.95 and 1.80 for PyVRP, which shows the size of the run-to-run noise. The lab will measure these again in its own sandbox, and those are the numbers the agents must beat."),
);

children.push(
  H1("5. Running it"),
  P("Open the Anaconda PowerShell Prompt and type these commands one at a time. The first two switch your artemis folder to the new branch, the third installs PyVRP, and the fourth checks everything on your computer and then starts the lab in the cloud."),
  Cmd("cd C:\\Users\\hales\\artemis"),
  Cmd("git fetch"),
  Cmd("git checkout cvrp-lab"),
  Cmd("pip install -r requirements-cvrp.txt"),
  Cmd("python scripts/run_cvrp.py"),
  P("The check takes about a minute. The lab then runs for roughly two to four hours, with a spending cap of 40 dollars on Claude usage plus the Modal sandbox time, the same budget as the solar run. You can close the window at any point; the lab keeps running, and the window prints the command that reconnects to it. When the lab finishes, its report is saved under the runs folder. Send it to me and I will check every number against the lab's ledger and commit the final solver to the branch."),
);

children.push(
  H1("6. After the run: hunting for a record"),
  P("Once the final solver is on the branch, one command gives it long runs on a hunt problem, eight independent attempts at once on Modal, and has the frozen judge check the best answer:"),
  Cmd("modal run lab/cvrp/hunt.py --instance X-n1001-k43 --minutes 60 --seeds 8"),
  P("Each attempt uses one processor core for the time you give it, so an hour with eight attempts is eight core-hours of Modal computing. I have not quoted a price because Modal's rates can change; please check your Modal billing page after a first short hunt. If the judge ever reports that a route set beats the best-known cost, we compare it with the live CVRPLIB table before claiming anything, because our snapshot may be a few weeks behind, and then submit it to CVRPLIB with the routes attached so anyone can verify it."),
);

children.push(
  H1("7. Decisions for you to confirm"),
  P("Three choices are recorded in the decisions log as mine, pending your approval: the 40 dollar spending cap, the time rule of three seconds per hundred customers, and the noise rule for keeping an idea. If you would like a longer or cheaper run, any of them can be changed before launch with a one-line edit, and the change will appear in the judge's fingerprint so it stays visible in every result."),
);

children.push(
  H1("Sources"),
  source("Uchoa et al., New benchmark instances for the CVRP, EJOR 257(3):845-858 (2017)", "https://doi.org/10.1016/j.ejor.2016.08.012"),
  source("CVRPLIB", "http://vrp.galgos.inf.puc-rio.br/"),
  source("PyVRP instances mirror (pinned commit 7474b06)", "https://github.com/PyVRP/Instances"),
  source("PyVRP", "https://github.com/PyVRP/PyVRP"),
  source("Artemis routing program", "https://github.com/alessoh/artemis/tree/cvrp-lab/lab/cvrp"),
);

const doc = new Document({
  creator: "Claude", title: "Artemis Routing Program Runbook",
  styles: {
    default: { document: { run: { font: BODY_FONT, size: 21, color: INK } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: HEAD_FONT, color: NAVY },
        paragraph: { spacing: { before: 420, after: 180 }, outlineLevel: 0, keepNext: true } },
    ],
  },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "Artemis  ·  Routing Program", font: HEAD_FONT, size: 16, color: MUTED })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: HEAD_FONT, size: 16, color: MUTED })] })] }) },
    children,
  }],
});
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync("Artemis_Routing_Program.docx", buf); console.log("written"); });
