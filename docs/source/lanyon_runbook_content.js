// Content for "Artemis Lanyon Audit: Runbook". Appended to guide_helpers.js at build time.
const children = [];
const Code = (text) => new Paragraph({
  spacing: { before: 60, after: 60 }, indent: { left: 360 },
  children: [new TextRun({ text, font: "Consolas", size: 19, color: INK })],
});

children.push(
  new Paragraph({ spacing: { before: 600, after: 120 }, children: [new TextRun({ text: "ARTEMIS  LANYON AUDIT", font: HEAD_FONT, size: 22, bold: true, color: TEAL, characterSpacing: 120 })] }),
  new Paragraph({ spacing: { after: 160 }, children: [new TextRun({ text: "Checking Lanyon's 72 Solver Specifications Against Their True Wave Speeds: Runbook", font: HEAD_FONT, size: 36, bold: true, color: INK })] }),
  new Paragraph({ spacing: { after: 400 }, children: [new TextRun({ text: "What the lab will do, what has been built and checked, and how to launch it from your computer", font: BODY_FONT, size: 24, italics: true, color: MUTED })] }),
);

children.push(
  H1("What this program does"),
  P("Lanyon AI's seven solver repositories hold 72 specifications, each pairing a set of physics equations with a numerical method, from which Lanyon generates C code and Lean proofs. Each specification lists the speeds at which its waves travel, and its method uses a dissipation speed built from them to stay stable. Lanyon's proofs never check either against the true wave speeds, the eigenvalues of the Jacobian of the specification's own flux. This program checks both, for every specification and every direction, 144 tasks in all, under the Artemis rules: a frozen judge, hypotheses and predictions committed before any checking code existed, a final run on a secret seed, and an independent check against Lanyon's own compiled C code."),
  P("The pre-registration fixes three hypotheses. H1 says the census of all 72 specifications matches four predictions written in advance. H2 says the lab's agents, searching adversarially, find points at least as bad as the census finds for every failing task. H3 says every failure found is present in the C code Lanyon actually ships, not only in the specification. The agents' job is H2 and the explanations: for each failing family, why it fails and under what conditions."),
);

children.push(
  H1("What has been built and checked"),
  P("The judge reads Lanyon's Racket specifications directly, with a small reader written for the subset of Racket they use, and turns every formula into exact symbolic algebra. Because every flux is a rational function and every sample is an exact binary number, the Jacobian at a point is an exact rational matrix, and its eigenvalues are found exactly, with their multiplicities. A sandbox, tested with deliberately hostile code, stops the agents' search code from reading files, starting processes or reaching the network, and a static check refuses dangerous code before it runs. Lanyon's repositories are fetched at pinned commits and fingerprinted, never copied into ours, because one of them has no licence."),
  P("Building it caught a bug worth recording. The first version of the exact check let a floating-point number into the supposedly exact Jacobian, which made the compressible Euler specifications appear to fail. It was found because the results looked wrong, traced, fixed, and documented in the implementation notes on the branch. An independent reviewer that did not write the code then audited the whole harness. It confirmed the core, including the reality of the MHD failure against the textbook formula to 50 digits, and it found two serious problems: the check against Lanyon's C code used the wrong function names for 27 of the 72 specifications, and nothing stopped a search from leaving the sampling box to win trivially. Both are fixed, along with six smaller issues, among them keeping the final seed away from the agents' code and saving the final results step by step. A full rehearsal of the final procedure on a test seed then ran cleanly in under ten minutes."),
);

children.push(
  H1("What is already known"),
  P("To test the harness, the census was run on development and test seeds. The results are therefore known before the lab runs, and the implementation notes say so. Of the 72 specifications, 57 pass both checks. All six ideal MHD specifications and all six curved-spacetime Maxwell specifications list wave speeds that are not the eigenvalues of their own flux, and those twelve plus the three flat-space hyperbolic Maxwell specifications have a dissipation speed that can fall below the fastest wave. The C kernels reproduce every one of those failures. Two of the four predictions held and two did not: the curved-spacetime specifications fail more widely than predicted, which is exactly what pre-registration is for."),
  P("An exploratory check with the speed of light fixed to one, the units Lanyon evidently intends, separates the failures that matter in practice from those that do not. The flat-space and standard curved-spacetime Maxwell specifications are then sound; the six MHD specifications and the three curved-spacetime hyperbolic Maxwell specifications still fail both checks."),
);

children.push(
  H1("How to launch the run"),
  P("The run needs your Omnigent server and keys, as before, so it starts from your computer. Open Anaconda PowerShell in your artemis folder, activate the artemis environment, and run these commands. The check step fetches Lanyon's seven repositories (this needs Git, which you have), verifies them against the fingerprints, and runs the harness once; it takes a few minutes. The launch step then starts the six-agent lab in a Modal sandbox and streams its progress."),
  Code("conda activate artemis"),
  Code("git fetch origin"),
  Code("git checkout lanyon-audit"),
  Code("pip install -r requirements-lanyon-audit.txt"),
  Code("python scripts/run_lanyon_audit.py"),
  P("The lab uses the same team and limits as the earlier runs: Claude Opus 5.5 for the lead, the Planner, the Experimenters, the Skeptic and the Scribe, Claude Haiku 4.5 for the Scout, a spending limit of 60 dollars and a cap of 700 tool calls. Each evaluation takes about two minutes, so the run should take a few hours. If anything stops with a message beginning STOPPED, send me a screenshot; no secret is printed. If you would rather use other models, the model names are on one line in each file under lab/agents/lanyon_audit_lab."),
);

children.push(
  H1("When the run finishes"),
  P("Send me the lab's final message or the session number. I will rebuild the frozen search from it, confirm its fingerprint, and run the final step once on the secret seed, which is stored privately in the project and has never been used. That step runs the census for H1, the lab's search for H2, compiles Lanyon's C kernels for H3, and repeats the c = 1 analysis. You will then have a results report and, with real Artemis results in hand, an updated letter to Drs. Gorard, Hakim and Juno."),
);

const doc = new Document({
  creator: "H. P. Alesso", title: "Artemis Lanyon Audit: Runbook",
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
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync("../Artemis_Lanyon_Audit_Runbook.docx", buf); console.log("written"); });
