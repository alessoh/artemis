// Content for "Artemis and Lanyon's Verified Solvers". Appended to guide_helpers.js at build time.
const children = [];

children.push(
  new Paragraph({ spacing: { before: 600, after: 120 }, children: [new TextRun({ text: "ARTEMIS  PROPOSAL", font: HEAD_FONT, size: 22, bold: true, color: TEAL, characterSpacing: 120 })] }),
  new Paragraph({ spacing: { after: 160 }, children: [new TextRun({ text: "Artemis and Lanyon's Verified Maxwell Solvers: How to Combine Them, and Research Worth Doing", font: HEAD_FONT, size: 36, bold: true, color: INK })] }),
  new Paragraph({ spacing: { after: 400 }, children: [new TextRun({ text: "Six research programs that join Artemis's pre-registered agent laboratory to Lanyon AI's proof-carrying solvers, 30 October 2026", font: BODY_FONT, size: 24, italics: true, color: MUTED })] }),
);

children.push(
  H1("The short answer"),
  P("Lanyon and Artemis solve opposite halves of the same problem. Lanyon makes a single piece of scientific code trustworthy by generating it together with a Lean proof from one specification, but it does not search, experiment or ask open questions. Artemis lets AI agents search and experiment freely while a frozen judge, pre-registration and a sealed test keep the results honest, but its judges so far have been statistical. Put together, Lanyon supplies kernels whose formulas are proven and a proof checker that no agent can argue with, and Artemis supplies the disciplined search. That fits the direction set for Artemis on 22 October, which was to point it at problems whose answers a third party checks: the Lean kernel is about the strictest third-party checker there is."),
  P("The best first program is small and concrete. Your explainer found that the perfectly hyperbolic specification allows divergence-cleaning waves faster than the Lax-Friedrichs speed the method assumes, which makes the scheme unstable when c is greater than one; I confirmed from the specification that the parameters may reach c while the method uses |c|. An Artemis program could map exactly where the kernels are stable, find the simplest corrected rule, and finish with a Lean proof of the corrected bound, all within a week of computing on ordinary processors. Five further programs, described below, extend the same pattern to the missing theorems, to rounding error, to tuning the divergence cleaning without hand adjustment, to Lanyon's eight other solver families, and in the longer run to using a Lanyon-style specification to build Artemis's own harnesses."),
);

children.push(
  H1("What each side brings"),
  P("Lanyon's MaxwellEquations repository holds, for each of six variants of Maxwell's equations in one to three dimensions, a Racket specification, a C solver kernel and a Lean 4 file with 13 theorems per direction, 156 in all, establishing for exact real numbers that the interface formulas conserve flux, vanish when nothing changes and reconstruct linear data exactly. It carries the MIT licence, which removes the licensing problem we met with the UN-CCD code. Since July Lanyon has published eight more repositories in the same style, covering ideal magnetohydrodynamics, isothermal and compressible Euler, Burgers, advection and advection-diffusion, the electrostatic Vlasov equation in up to six phase-space dimensions, and Maxwell's equations in curved spacetime, and its founders' BEACONS paper (arXiv:2602.14853) extends the idea to neural PDE solvers with certified error bounds. What the repositories do not contain is equally important: there is no time-stepping driver, no proof about rounded arithmetic, and no theorem about stability over many steps, convergence or whether divergence cleaning works. Those gaps are where research can be done."),
  P("Artemis brings the method for doing that research honestly. A frozen harness, fingerprinted and checked before every evaluation, holds the data and the metric; agents may change only one file; a Skeptic can veto a change; a change is kept only if it beats the incumbent by a margin fixed in advance; and the final claim is tested once on sealed data and then reproduced. Applied here, the harness would wrap Lanyon's kernels in a driver that Artemis writes and freezes, and the judge would be either a numerical measurement on sealed test cases or the Lean kernel itself."),
  table(
    [2200, 3580, 3580],
    ["Artemis file", "Numerical programs", "Proof programs"],
    [
      ["harness (frozen)", "Lanyon's C kernels, a time-stepping driver, test cases with exact solutions, the metric", "A pinned Lean and Mathlib toolchain, Lanyon's definitions, the target theorem statements, a checker that rejects sorry, admit, axiom and native_decide"],
      ["experiment (mutable)", "The agent's rule: parameter limits, wave-speed choice, time-step rule, reformulated arithmetic", "The agent's proof file"],
      ["program.md (human)", "Question, hypotheses and pass marks, written before the run", "The list of statements to prove, written before the run"],
    ],
  ),
  Caption("Table 1. How the two kinds of program map onto the Artemis three-file pattern."),
);

children.push(
  H1("Six research programs"),
  P("Table 2 lists the programs in the order I would run them. Each is described below with its question, its judge, the hypothesis it would pre-register and an honest note on what is already known."),
  table(
    [2600, 2500, 1500, 2760],
    ["Program", "Judge", "Effort", "Main value"],
    [
      ["1. The wave-speed gap: a stability atlas and a corrected proof", "Numerical, on a sealed parameter grid; then Lean", "About a week", "A confirmed fix, offered to Lanyon"],
      ["2. Proving the missing theorems", "Lean kernel", "Two to four weeks", "Machine-checked versions of classical results, tied to these exact kernels"],
      ["3. The floating-point gap", "Exact rational arithmetic", "Two to three weeks", "Error bounds for the code the computer actually runs"],
      ["4. Choosing the cleaning speeds without hand tuning", "Numerical, on sealed cavity problems with exact solutions", "Two to three weeks", "A tested rule for chi and gamma, the analogue of the UN-CCD alpha result"],
      ["5. Auditing Lanyon's eight other solver families", "Numerical and Lean", "One to two weeks per family", "A reproducible review of verified physics code"],
      ["6. A Lanyon-style specification for Artemis harnesses", "Regenerating an existing harness", "Longer term", "Harnesses whose metrics carry their own proofs"],
    ],
  ),
  Caption("Table 2. Proposed programs. Effort assumes the same computing scale as the earlier Artemis programs, which ran on ordinary processors in Modal sandboxes."),
);

children.push(
  H2("1. The wave-speed gap"),
  P("The specification allows the cleaning parameters chi and gamma to reach c, so the cleaning waves can travel at up to c squared, while the Lax-Friedrichs splitting assumes no wave is faster than |c|. Your explainer's probe found the one-dimensional scheme blowing up by a factor of more than 10^67 at c = 2 with chi = gamma = 2, even with a correctly chosen time step. The harness would freeze a driver built only from the repository's own fluctuation functions, a set of smooth and discontinuous starting fields, and a sealed grid of values of c, chi, gamma, time step and dimension. The agents would propose a rule, such as a cap on chi and gamma or a Lax-Friedrichs speed of c times the largest of one, chi and gamma, and the judge would score how often the rule keeps the solution bounded while losing the least accuracy. The pre-registered hypothesis would be that the corrected speed restores stability on every sealed case at no cost when c equals one. The final step is a Lean theorem stating that the method's speed bounds every eigenvalue, the statement the current WaveStability theorem appears to intend but does not make. The underlying fact, that Rusanov's method needs a speed at least as large as the fastest wave, is textbook, so the value lies in the careful demonstration, the fix and the proof, which would make a natural, friendly contribution to Lanyon's repository."),
);

children.push(
  H2("2. Proving the missing theorems"),
  P("The explainer lists properties no theorem in the repository establishes: true hyperbolicity, meaning a complete set of eigenvectors rather than real-valued speeds; that the minmod reconstruction is total variation diminishing, which Lanyon's own note claims; that the first-order scheme is stable under the CFL condition; and that the cleaning fields actually carry divergence errors away. An Artemis proof program would fix the exact statements in Lean before the run, pin Lean and Mathlib versions, and let the agents write proofs, with the Lean kernel as the only judge and the usual escape hatches forbidden. The metric is simply how many pre-registered statements are proved, so there is nothing to argue about afterwards. The work is hard but well defined: the TVD and linear stability results are classical on paper, and the contribution is machine-checked versions tied to these exact kernels. One practical point needs checking first: your explainer could not reach the servers that distribute Lean and Mathlib from Claude's workspace, so the toolchain would have to be built into the Modal image."),
);

children.push(
  H2("3. The floating-point gap"),
  P("Lanyon's proofs treat every number as an exact real, while the C code rounds to about sixteen digits; the explainer showed the self-checks failing about half the time once field values reach a billion or c takes its SI value. A numerical program would let the agents search for inputs that maximise the gap between the C result and the exact result, computed with rational arithmetic in the frozen judge, and then propose reformulations, such as scaling or regrouping, that reduce the worst case without changing the mathematics. The pass mark would be a reduction of the worst-case relative error on a sealed set of adversarial and random inputs. Established tools for rigorous rounding-error bounds, such as Gappa and FPTaylor, could then certify the improved formulas. This addresses the most important limit on the phrase end-to-end formally verified."),
);

children.push(
  H2("4. Choosing the cleaning speeds without hand tuning"),
  P("Divergence cleaning works only if chi and gamma are chosen well, and in practice they are set by hand. This is the same kind of question as UN-CCD's alpha, where Artemis found a label-free rule that beat the authors' hand tuning on sealed data. The harness would run Lanyon's two- and three-dimensional kernels on electromagnetic cavity problems whose exact solutions are known, such as the resonant modes of a metal box, with deliberate divergence errors introduced, and score the long-run divergence error and the error against the exact solution. The agents would propose rules for chi and gamma from the grid and the problem alone, and the sealed test would use cavity shapes, resolutions and run lengths not seen during the search. There is substantial prior work, from Munz and colleagues in 2000 and on the closely related cleaning method for magnetohydrodynamics by Dedner and colleagues in 2002, so a literature search must come first and the claim must be framed as a tested rule for these kernels, not a new method."),
);

children.push(
  H2("5. Auditing Lanyon's other solver families"),
  P("The eight other repositories raise sharper questions than Maxwell, because their equations are nonlinear. For compressible Euler and magnetohydrodynamics the decisive properties are whether density and pressure stay positive and whether the scheme respects entropy; for Burgers it is whether shocks travel at the right speed; for the Vlasov solver in up to six dimensions it is conservation of particles and energy. Artemis would run each family through the same review your explainer carried out by hand, recounting the claims, compiling and exercising the code, checking the physics symbolically and probing stability, and then pre-register tests of the properties the proofs do not cover. This is the reproduce-and-extend pattern of the UN-CCD work, applied to a company that welcomes scrutiny of its claims, and a systematic, public audit of AI-generated verified physics code would be useful to the whole field."),
);

children.push(
  H2("6. A Lanyon-style specification for Artemis harnesses"),
  P("The research direction of 22 October proposed a harness kit with a Compiler agent, judged by whether it can regenerate the routing harness from one paragraph. Lanyon's method suggests a stronger version: write the metric and the data rules of a harness as a short formal specification, and generate both the harness code and proofs of its key properties, for example that the metric is symmetric, bounded and invariant to the order of the data, which would have caught the Cremona ordering leak by construction. Lanyon's generator is not public, so this would be Artemis's own, simpler version, and it is a longer-term idea rather than a first program."),
);

children.push(
  H1("Recommended order"),
  P("I would start with Program 1, because it is quick, its outcome is certain to be useful and it builds the frozen driver every later numerical program needs. Program 2 should be prepared alongside it, beginning with the one-week task of getting a pinned Lean and Mathlib toolchain to run inside the Modal sandbox and confirming that all 156 of Lanyon's proofs check, which your explainer could not do. Program 4 then follows naturally from the driver and is the most likely to produce a result of the UN-CCD kind, and Program 3 can run in parallel at any point. Programs 5 and 6 are best treated as a second season. Whatever is found should go to Lanyon in the same collegial way as the note to the UN-CCD authors, since several questions, such as which parameter range the generator intends, only they can answer."),
  P("Two small corrections to the explainer are worth making before it is shared. The repository has two commits, an initial commit on 19 July and the main commit on 20 July, not one. And Lanyon has since published eight more repositories, which places MaxwellEquations as the first of a series rather than a one-off."),
);

children.push(
  H1("A decision for you: which models"),
  P("Each program needs agents, and the proof programs in particular depend on the model. For the agents I would suggest choosing among closed models such as Claude Opus 5.5, which has run every Artemis program so far, and the current GPT and Gemini frontier models, with a model from a different vendor as the Skeptic so that it does not share the Experimenters' blind spots, as the research direction recommended. For Lean proving there are also open models trained specifically for it, such as the DeepSeek-Prover, Kimina-Prover and Goedel-Prover families; I know of these from releases up to mid-2026 and would check their current versions and licences before choosing. A mix, a strong closed model as planner and an open prover model as a cheap, fast proof search, is likely to give the best results per dollar. Please tell me which models you would like, and whether you want Program 1 built next."),
);

children.push(
  H1("Sources"),
  source("Lanyon AI, MaxwellEquations repository (commit 801558f, 20 July 2026)", "https://github.com/lanyonai/MaxwellEquations"),
  source("Lanyon AI, organisation page listing the nine solver repositories", "https://github.com/lanyonai"),
  source("Gorard, Hakim and Juno, BEACONS: Bounded-Error, Algebraically-Composable Neural Solvers for PDEs, arXiv:2602.14853", "https://arxiv.org/abs/2602.14853"),
  source("Lanyon AI, Benchmarking Lanyon against Frontier Models: Linear PDEs", "http://lanyon.ai/research/linear-benchmarking/"),
  source("Lanyon AI, Benchmarking Lanyon against Frontier Models: Nonlinear PDEs", "http://lanyon.ai/research/nonlinear-benchmarking/"),
  source("Lanyon AI emerges from stealth (press release)", "https://www.prnewswire.com/news-releases/lanyon-ai-emerges-from-stealth-to-build-the-future-of-scientific-and-technical-computing-302852383.html"),
  source("Julia Discourse discussion of Lanyon AI", "https://discourse.julialang.org/t/lanyon-ai-formal-verification-for-scientific-computing/139848"),
  P("Background: C.-D. Munz, P. Omnes, R. Schneider, E. Sonnendrücker and U. Voß, Divergence correction techniques for Maxwell solvers based on a hyperbolic model, Journal of Computational Physics 161 (2000); A. Dedner, F. Kemm, D. Kröner, C.-D. Munz, T. Schnitzer and M. Wesenberg, Hyperbolic divergence cleaning for the MHD equations, Journal of Computational Physics 175 (2002); R. J. LeVeque, Finite Volume Methods for Hyperbolic Problems, Cambridge University Press (2002); and the Artemis research direction of 22 October 2026 in the project."),
);

const doc = new Document({
  creator: "H. P. Alesso", title: "Artemis and Lanyon's Verified Maxwell Solvers",
  styles: {
    default: { document: { run: { font: BODY_FONT, size: 22, color: INK } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: HEAD_FONT, color: NAVY },
        paragraph: { spacing: { before: 360, after: 160 }, outlineLevel: 0, keepNext: true } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: HEAD_FONT, color: TEAL },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1, keepNext: true } },
    ],
  },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: HEAD_FONT, size: 16, color: MUTED })] })] }) },
    children,
  }],
});
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync("../Artemis_Lanyon_Maxwell_Research_Proposals.docx", buf); console.log("written"); });
