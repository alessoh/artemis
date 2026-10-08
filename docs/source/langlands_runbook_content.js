// Content for "Artemis Langlands Program Runbook". Appended to guide_helpers.js at build time.
const children = [];
const Cmd = (t) => new Paragraph({ spacing: { after: 80 }, indent: { left: 540 },
  children: [new TextRun({ text: t, font: "Consolas", size: 20, color: INK })] });

children.push(
  new Paragraph({ spacing: { before: 1400, after: 120 }, children: [new TextRun({ text: "ARTEMIS", font: HEAD_FONT, size: 22, bold: true, color: TEAL, characterSpacing: 120 })] }),
  new Paragraph({ spacing: { after: 200 }, children: [new TextRun({ text: "The Langlands Program", font: HEAD_FONT, size: 52, bold: true, color: INK })] }),
  new Paragraph({ spacing: { after: 600 }, children: [new TextRun({ text: "Murmurations, the archimedean sign and local root numbers: what was built, what it can and cannot claim, and how to run it", font: BODY_FONT, size: 28, italics: true, color: MUTED })] }),
  new Paragraph({ border: { top: { style: BorderStyle.SINGLE, size: 6, color: NAVY, space: 8 } }, spacing: { after: 80 },
    children: [new TextRun({ text: "Branch langlands-lab of github.com/alessoh/artemis", font: HEAD_FONT, size: 20, color: INK })] }),
  new Paragraph({ spacing: { after: 80 }, children: [new TextRun({ text: "Thursday, October 8, 2026", font: HEAD_FONT, size: 20, color: MUTED })] }),
  new Paragraph({ spacing: { before: 1000 }, children: runs("You asked Artemis to run research direction R1 from your memo, \"Euler's identity and the Langlands program\", on a new branch. This document explains the two questions as the lab will test them, what the answers are likely to be, how the program is built and protected, what an independent audit found before any agent touched it, and the commands that start the run from your computer.", { size: 21, color: MUTED }) }),
  new Paragraph({ children: [new PageBreak()] }),
);

children.push(
  H1("1. The two questions"),
  P("Your memo starts from the observation that Euler's identity is the root number of the real place. For an elliptic curve over the rationals, the sign of the functional equation is minus the product of the local signs at the bad primes, and that leading minus sign is the contribution of the single real place. Over the field Q(\u221A5) there are two real places, so the same rule carries a plus sign. Murmurations, the oscillating averages of a\u209A first seen by He, Lee, Oliver and Pozdnyakov and explained by Zubrilina, are at leading order a correlation between a\u209A and that global sign."),
  P("**Part A** asks whether murmurations over Q(\u221A5) line up with the plus product of the finite local signs, the reverse of the rule over Q. It is a fixed measurement. The harness first reproduces the published pattern over Q for conductors from 1,000 to 4,999, then builds the same profile over Q(\u221A5) for conductor norms in the same range and measures how it correlates with the profile over Q. The primary statistic uses only semistable curves, whose finite signs the harness computes directly from the reduction at each bad prime, so no root-number routine enters the test."),
  P("**Part B** is your second question: rank 0 and rank 2 curves over Q both have global sign plus one, so their local signs have the same product, but does the vector of local signs itself depend on rank? The harness compares only curves that share the same conductor, so that the primes and their exponents are identical and only the signs differ. This is the part the agents work on, in the AutoResearch loop, looking for the clearest description of where any difference lives."),
);

children.push(
  H1("2. What to expect, honestly"),
  P("Part A is more a demonstration than a discovery. The rule that the global sign equals the product of local signs times minus one for each real place is Deligne's, and the data build already confirmed it for all 3,333 semistable classes over Q(\u221A5), together with rank parity for 4,602 of the 4,605 classes. So the flip is expected. On the small pilot range, below conductor norm 1,000, the correlation came out at 0.47 with a 95 percent interval of 0.27 to 0.61, in the predicted direction. The pilot also showed something less expected: the profile over Q(\u221A5) stays positive where the profile over Q turns negative, which suggests the pattern over the larger field may sit on a different scale of p divided by the conductor. That is worth a sentence in the report, not a claim."),
  P("Part B is genuinely open, and it already shows a small, real effect. On the training conductors alone, rank 2 classes have slightly more split multiplicative primes than rank 0 classes with the same conductor: a within-conductor AUC of 0.508, where 0.5 means no difference, with a z score of 5.7. Weighting each such prime by log p over p erases the effect, which hints that the direction depends on the size of the prime. For scale, the same measure reaches 0.97 when it is allowed to look at a\u209A at the good primes below 100, which the agents never see. So the signs carry a faint rank signal and a\u209A carries a strong one. The lab's job is to map the faint one."),
  P("I do not know of a published answer to the Part B question. A quick search found one closely related paper, \"Variations on murmurations\", which works over Q and weights murmurations by products of local root numbers over sets of places. The Scout is told to read it and report what it actually shows before the report claims anything is new."),
);

children.push(
  H1("3. How the program is built"),
  P("The program follows the same three-file pattern as the earlier runs. The frozen judge, harness.py, loads the data, runs every experiment in a clean process and computes every statistic. The agents may change only experiment.py, which defines one function that scores each curve from its conductor and local signs, and starts as the simple rule of counting split multiplicative primes. The instructions in program.md fix every definition before the first experiment, including the two hypotheses that the final test decides."),
  table([2400, 6960], ["Data", "What it holds"], [
    ["Cremona's tables", "Every isogeny class over Q with conductor below 500,000 and rank 0 or 2 (790,258 and 279,056 classes), pinned to one commit of the public ecdata repository."],
    ["Over Q, N < 5,000", "17,314 classes with a\u209A for every good prime up to the conductor, computed with PARI; local signs, global sign and rank parity checked for every class."],
    ["Over Q(\u221A5)", "Your LMFDB download of October 8: 4,605 isogeny classes with conductor norm below 5,000, with a\u209A at every degree-one prime, computed with PARI."],
  ]),
  Spacer(),
  table([2400, 2400, 4560], ["Split", "Conductors", "Use"], [
    ["Train", "below 300,000", "Free to explore and to train on"],
    ["Val", "300,000 to 399,999", "The loop's score; 40 evaluations and 16 recheck runs"],
    ["Test", "400,000 to 499,999", "Scored once, at the end, and never seen by anyone before"],
  ]),
  Spacer(),
  P("The final test decides two pre-registered hypotheses, each at a one-sided p below 0.01 by both a normal approximation and 2,000 within-conductor permutations. The first is that the frozen simple rule separates rank 2 from rank 0 within a conductor. It was fixed before any agent ran, so it is a clean confirmatory test of the training-set observation. The second is the same claim for the lab's own best experiment. My expectation is that the first will be supported, because the effect on the validation range, which I saw while testing the harness, is at least as large, and that the second will be supported too, with the open question being whether the agents find a sharper rule than the simple one."),
);

children.push(
  H1("4. What the audit found"),
  P("Before committing anything I asked a separate agent, which had not written the code, to attack it. Its most important finding was a real leak: within each conductor, Cremona's tables list classes in an order that is correlated with rank, strong enough that position alone gave a within-conductor AUC of 0.564, far above anything the signs give. The harness now hands each distinct pair of conductor and sign pattern to the experiment exactly once, so position carries nothing, and every class with that pattern receives the same score. This also makes every result exactly reproducible."),
  P("The audit also found ways around the code check, such as a star import, attribute lookup through the operator module and a single enormous integer, and a gap between checking a file and running it. All are closed: the check is now an allowlist of modules and submodules, the exact checked bytes are run and archived, and the process that runs an experiment refuses at run time to open files outside the Python installation, to start processes or to use the network. A second audit pass confirmed every fix. Because the labels are public mathematics, the final safeguard is not secrecy but the record: archived code for every trial, the full transcript of every agent command, a ledger committed after each wave, and a re-run of the final test by us after the lab finishes."),
);

children.push(
  H1("5. How to run it"),
  P("In the Anaconda PowerShell Prompt, from your artemis folder, these commands switch to the new branch, install the three small libraries it needs and start the lab. The last command first checks the harness on your computer, which takes about a minute, then starts the six agents in a Modal sandbox and shows their progress in the window."),
  Cmd("cd C:\\Users\\hales\\artemis"),
  Cmd("git fetch"),
  Cmd("git checkout langlands-lab"),
  Cmd("git pull"),
  Cmd("pip install -r requirements-langlands.txt"),
  Cmd("python scripts/run_langlands.py"),
  P("If you close the window the lab keeps running in the cloud, and you can reconnect with the watch command and the session number the script prints. When the run finishes, the script saves the report and the full transcript under the runs folder. Please keep that folder private, because transcripts can contain keys."),
  Cmd("python scripts/run_langlands.py watch SESSION_ID"),
  P("The spending limit is 60 dollars and the loop stops after 40 validation evaluations. Each evaluation takes about a minute of computing, so I expect the run to take a few hours and to cost less than the limit, but I cannot promise either figure in advance. Both limits, and the stopping rule that needs at least 25 evaluations before a plateau may end the loop, are recorded in the decisions log as my choices pending your approval; any of them can be changed with a one-line edit before launch."),
);

children.push(
  H1("6. After the run"),
  P("Send me the saved report and transcript, as you did for the routing runs. I will read the archived code of every kept trial, search the transcript for any command that touched the data outside the harness, and re-run the final test independently on the promoted experiment to confirm the numbers. Only then would I suggest describing a result outside the lab, and the wording will follow what the held-out test supports and no further."),
);

children.push(
  H1("Sources"),
  source("P. Alesso, Euler's identity and the Langlands program (research memo, 2026)", "https://www.researchgate.net/publication/414016686_Euler_Identity_and_Langlands_Program"),
  source("He, Lee, Oliver and Pozdnyakov, Murmurations of elliptic curves (2022)", "https://arxiv.org/abs/2204.10140"),
  source("Zubrilina, Murmurations (2023)", "https://arxiv.org/abs/2310.07681"),
  source("Variations on murmurations (2025)", "https://arxiv.org/abs/2505.01093"),
  source("J. E. Cremona, elliptic curve data (ecdata, commit 25cec5e)", "https://github.com/JohnCremona/ecdata"),
  source("LMFDB, elliptic curves over Q(\u221A5)", "https://www.lmfdb.org/EllipticCurve/2.2.5.1/"),
  source("PARI/GP", "https://pari.math.u-bordeaux.fr/"),
  source("Artemis Langlands program", "https://github.com/alessoh/artemis/tree/langlands-lab/lab/langlands"),
);

const doc = new Document({
  creator: "Claude", title: "Artemis Langlands Program Runbook",
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
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "Artemis  \u00B7  Langlands Program", font: HEAD_FONT, size: 16, color: MUTED })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: HEAD_FONT, size: 16, color: MUTED })] })] }) },
    children,
  }],
});
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync("Artemis_Langlands_Program.docx", buf); console.log("written"); });
