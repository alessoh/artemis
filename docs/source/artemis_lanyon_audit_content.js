// Content for "Verifying the Verified: an Artemis-Lanyon audit proposal". Appended to guide_helpers.js at build time.
const children = [];

children.push(
  new Paragraph({ spacing: { before: 600, after: 120 }, children: [new TextRun({ text: "ARTEMIS  PROPOSAL", font: HEAD_FONT, size: 22, bold: true, color: TEAL, characterSpacing: 120 })] }),
  new Paragraph({ spacing: { after: 160 }, children: [new TextRun({ text: "Verifying the Verified: A Pre-Registered Audit of AI-Generated, Formally Verified Physics Solvers", font: HEAD_FONT, size: 36, bold: true, color: INK })] }),
  new Paragraph({ spacing: { after: 400 }, children: [new TextRun({ text: "An Artemis program on Lanyon AI's seven solver repositories, with preliminary results, 31 October 2026", font: BODY_FONT, size: 24, italics: true, color: MUTED })] }),
);

children.push(
  H1("The proposal in brief"),
  P("Lanyon AI generates physics solvers together with Lean proofs from one specification and describes them as end-to-end formally verified. Its seven solver repositories hold 72 specifications, from Maxwell's equations to magnetohydrodynamics, compressible flow and plasma kinetics, with 2,100 machine-checked theorems and no shortcuts in any proof. The question this program asks is the one every user of such code needs answered: does a proof about the code guarantee that the simulation is right, and where exactly does the guarantee stop? Artemis would answer it for all 72 specifications with three judges no agent can sway, a symbolic checker of each specification's physics, a frozen simulation driver running standard test problems with known answers, and the Lean proof checker, under hypotheses fixed in advance."),
  P("I recommend this over the six programs of yesterday's proposal because it is the one most likely to yield important, publishable science, and the reason is that the first finding already exists. Checking Lanyon's magnetohydrodynamics specification this morning, I found that its wave-speed formula is wrong in all six variants, that the formula underestimates the fastest wave at about half of all interfaces, and that on a standard shock-tube problem viewed from a moving frame the error lets the pressure go negative while the correct speed keeps it positive. None of the 156 theorems in that repository can catch this, because none of them connects the listed wave speeds to the physics. A paper built on a pre-registered, independent audit of AI-generated verified scientific code, with a concrete, reproducible defect of this kind at its centre and a general fix for the whole class, would be timely and useful well beyond Lanyon."),
);

children.push(
  H1("Lanyon's repositories"),
  P("The lanyonai organisation on GitHub lists nine repositories, as of today. Seven are verified-solver families; the other two are LanyonScripts, which holds the computer-algebra scripts behind Lanyon's research notes, and a fork of the Gkeyll plasma code. If you see six, that may be the pinned repositories at the top of the page. Table 1 lists the seven families. Every one of them uses the same template of thirteen theorems per direction, and I found no sorry, admit, axiom or native_decide in any proof file. All carry the MIT licence except AdvectionDiffusion, which has no licence file and would need Lanyon's permission before its code is reused."),
  table(
    [2700, 1300, 1300, 4060],
    ["Repository (last commit)", "Specs", "Theorems", "Equations"],
    [
      ["MaxwellEquations (20 Jul)", "6", "156", "Maxwell and perfectly hyperbolic Maxwell, 1D to 3D"],
      ["ElectrostaticVlasov (20 Jul)", "6", "312", "Electrostatic Vlasov, 1x1v to 3x3v phase space"],
      ["GeneralRelativisticMaxwell (27 Jul)", "6", "156", "Maxwell in curved spacetime, with and without cleaning"],
      ["CompressibleEuler (10 Aug)", "6", "156", "Isothermal and ideal-gas Euler, 1D to 3D"],
      ["IdealMHD (27 Aug)", "6", "156", "Ideal MHD, with and without divergence cleaning"],
      ["AdvectionDiffusion (8 Sep)", "21", "582", "Advection and advection-diffusion, finite volume and DG"],
      ["BurgersEquation (9 Sep)", "21", "582", "Inviscid and viscous Burgers, finite volume and DG"],
      ["Total", "72", "2,100", ""],
    ],
  ),
  Caption("Table 1. Lanyon's solver repositories, counted from fresh clones on 31 October 2026."),
);

children.push(
  H1("What is already known"),
  P("Two specification-level defects have been found so far, both by hand and neither yet pre-registered. The first is the one in your explainer: the perfectly hyperbolic Maxwell specification allows divergence-cleaning waves faster than the speed the Lax-Friedrichs method assumes, so the scheme is unstable when c exceeds one with large cleaning parameters. That defect lies outside the scaled units Lanyon evidently intends."),
  P("The second is new and more serious. In the ideal MHD specification the Alfvén speed is written as the flow velocity minus |B| divided by the square root of the density, so the flow speed is counted twice in the listed Alfvén waves; and the fast and slow speeds use the total magnetic field where the standard formula uses its normal component. The listed fast speed therefore collapses to the larger of the sound speed and this mis-defined Alfvén speed, which in general understates the true fast speed whenever the field has a component across the direction of travel. I built the exact Jacobian of the specification's own flux symbolically and compared its eigenvalues with the listed speeds. Table 2 gives the result: the listed speeds are wrong in every state tested, and the speed that sets the method's numerical dissipation is too small at about half of all interfaces. The same construction appears in all six MHD specifications, and the C kernel computes exactly the same expression."),
  table(
    [6200, 3160],
    ["Check on IdealMHD (commit beeff1a)", "Result"],
    [
      ["States where listed speeds differ from the true Jacobian eigenvalues", "40,000 of 40,000"],
      ["States where the textbook fast speed matches the true bound (control)", "40,000 of 40,000"],
      ["Random interfaces where the method's speed is below the fastest wave", "10,429 of 20,000 (52.1%)"],
      ["Smallest ratio of the method's speed to the true fastest speed", "0.532"],
      ["Brio–Wu shock tube, left state", "0.789 of the true speed"],
      ["Brio–Wu with uniform flow u = 2, specification's speed", "Pressure goes negative (minimum −3.56)"],
      ["Same problem, textbook fast speed", "Stays positive (minimum 0.089)"],
    ],
  ),
  Caption("Table 2. Preliminary results. The shock-tube runs use a first-order Rusanov driver written by Claude on the specification's flux, with CFL 0.9; Lanyon's own driver is not public. Scripts and outputs are in lab/lanyon_audit/prelim on the main branch of the Artemis repository."),
  P("The moving-frame test is the telling one. Adding a uniform flow changes nothing physical, so a correct scheme must behave the same; the specification's formula breaks this Galilean invariance, and that is where it fails. The two defects share one cause: Lanyon's files define the flux Jacobian, but no theorem ties the listed wave speeds, or the speed the method uses, to its eigenvalues. The theorem called Hyperbolicity says only that each listed speed is a real number, and WaveStability compares the list with itself. A proof guarantees exactly what its statement says, and the statements stop one step short of the property that keeps the simulation stable."),
  P("Two cautions apply. My driver is first order and my own, and Lanyon's unpublished driver may use a smaller time step that hides the problem in practice; establishing how often the defect matters in realistic runs is part of what the program must measure. And I transcribed the formulas by hand; the program will parse every specification directly."),
);

children.push(
  H1("The Artemis program"),
  P("The program follows the Artemis pattern exactly. A frozen harness holds three judges. The first is a symbolic checker that reads each of the 72 Racket specifications, builds the flux Jacobian, compares its eigenvalues with the listed speeds, tests that the system has a full set of eigenvectors, and samples the states the specification allows to test whether the method's dissipation speed always bounds the fastest wave. The second is a frozen reference driver that runs Lanyon's own C kernels on a battery of standard problems with exact or well-established answers, listed in Table 3, together with metamorphic tests, the same problem shifted, rotated, mirrored or rescaled, which must give the same physics. The third is a pinned Lean and Mathlib toolchain that rejects any proof containing sorry, admit, axiom or native_decide."),
  table(
    [2400, 6960],
    ["Family", "Reference problems"],
    [
      ["Maxwell", "Resonant modes of a metal cavity (exact); divergence growth with and without cleaning"],
      ["Relativistic Maxwell", "Wald's exact solution for a uniform field around a rotating black hole"],
      ["Euler", "Sod and Lax shock tubes (exact Riemann solutions); isentropic vortex (exact, for order of accuracy)"],
      ["Ideal MHD", "Brio–Wu and Ryu–Jones shock tubes; circularly polarised Alfvén wave (exact); Orszag–Tang vortex"],
      ["Vlasov", "Linear Landau damping (damping rate −0.1533 at k = 0.5); two-stream instability growth"],
      ["Burgers", "Shock speed from the Rankine–Hugoniot condition; rarefaction and pre-shock solutions (exact)"],
      ["Advection-diffusion", "Translating and spreading Gaussian (exact)"],
    ],
  ),
  Caption("Table 3. The battery of reference problems, each also run in shifted, rotated or rescaled form."),
  P("The agents' file is where the search happens. Experimenters look adversarially for states, parameters and starting fields that break a solver, as the moving-frame shift broke the MHD one, and propose repairs; every claimed defect counts only if the frozen judge reproduces it from a minimal case, and the Skeptic can veto any claim. Before the run, program.md fixes three hypotheses and the complete final battery. H1, on consistency, counts how many of the 72 specifications list speeds equal to their Jacobian eigenvalues and use a dissipation speed that bounds them. H2, on consequence, asks whether replacing the defective speeds removes every positivity and stability failure on the battery at CFL 0.9 without loss of accuracy elsewhere. H3, on repair, asks whether a new theorem, that the method's speed is at least the magnitude of every eigenvalue of the Jacobian, can be proved in Lean for the corrected Maxwell and Euler specifications, with MHD as a stretch goal. The final battery is run once at the end and then reproduced by a separate session, as in every earlier program."),
);

children.push(
  H1("Why it is likely to be published"),
  P("Three features make a publishable result very likely rather than merely possible. First, the central finding already exists and is reproducible, so the program starts from a result and its job is to establish its extent and consequences. Second, every judge is deterministic and external: a symbolic computation, a test problem with a known answer, or a Lean proof, so referees can check every claim themselves. Third, the design is pre-registered, so both outcomes are informative: if the audit finds the other families sound, that is itself a useful independent confirmation of an important new approach, and the MHD defect and the general fix still stand."),
  P("The importance comes from timing. AI systems that write scientific code with formal guarantees are attracting investment and attention, and the field has few independent studies of what those guarantees deliver in practice. The paper's general lesson, that verification must tie a scheme's stability parameters to the physics of its equations and not only to its own definitions, applies to every such system, and the proposed theorem template is a concrete way to enforce it. The natural home is an arXiv preprint in computational physics or mathematical software, cross-listed to logic in computer science and artificial intelligence, followed by a journal in computational physics or a formal-methods venue; which fits best should be settled once the results are in."),
);

children.push(
  H1("Working with Lanyon"),
  P("This should be done with Lanyon, not at them. Before anything is posted, the findings should go privately to Jonathan Gorard, Ammar Hakim and James Juno, with the scripts and a reasonable period, around thirty days, to respond, fix the specifications and comment; inviting them to contribute to or co-author the paper may well strengthen it. Some questions only they can answer, for instance whether their simulation driver sets the time step from different speeds, which would change how often the defect matters in practice. Their research is open and its licence permits this work, and an independent audit that ends in corrected code and a stronger theorem template serves their goals as much as ours."),
);

children.push(
  H1("Plan, cost and risks"),
  P("The work fits in about four weeks. In the first week Artemis's harness is built: the specification parser and symbolic checker, the frozen driver with the reference battery, and the Lean toolchain inside the Modal image, which should first confirm that Lanyon's existing proofs check. The second week is the agents' run, the third the sealed battery, the independent reproduction and the Lean work, and the fourth the paper and the private report to Lanyon. Computing needs are modest, ordinary processors in Modal sandboxes, and model spending can be capped as before at around sixty to eighty dollars a run."),
  P("The main risks are manageable. Lanyon may fix the specifications quickly, which is a good outcome and does not affect the paper, since every finding is tied to a pinned commit. The MHD defect may matter less in Lanyon's own runs than in mine, which the program measures rather than assumes. A careful search of the literature on verified numerical software must precede any claim of novelty. And the Lean repair theorem for MHD involves nested square roots and may prove hard, which is why it is a stretch goal."),
);

children.push(
  H1("Decisions for you"),
  P("I need three decisions to start. The first is whether to go ahead with this program. The second is the models: for the agents I suggest Claude Opus 5.5, with a model from another company, a current GPT or Gemini model, as the Skeptic; for the Lean work, an open prover model such as the DeepSeek-Prover, Kimina-Prover or Goedel-Prover families could run alongside, after checking their current versions. The third is when to contact Lanyon: I suggest after the symbolic audit of all 72 specifications, in the first or second week, so that the report covers every family."),
);

children.push(
  H1("Sources"),
  source("Lanyon AI on GitHub (nine repositories)", "https://github.com/lanyonai"),
  source("IdealMHD, commit beeff1a, specification and C kernel examined", "https://github.com/lanyonai/IdealMHD"),
  source("MaxwellEquations, commit 801558f", "https://github.com/lanyonai/MaxwellEquations"),
  source("Preliminary probe scripts and outputs (Artemis main branch)", "https://github.com/alessoh/artemis/tree/main/lab/lanyon_audit/prelim"),
  source("Gorard, Hakim and Juno, BEACONS, arXiv:2602.14853", "https://arxiv.org/abs/2602.14853"),
  P("Background: M. Brio and C. C. Wu, An upwind differencing scheme for the equations of ideal magnetohydrodynamics, Journal of Computational Physics 75 (1988); D. Ryu and T. W. Jones, Numerical magnetohydrodynamics in astrophysics, Astrophysical Journal 442 (1995); G. Tóth, The ∇·B = 0 constraint in shock-capturing MHD codes, Journal of Computational Physics 161 (2000); R. M. Wald, Black hole in a uniform magnetic field, Physical Review D 10 (1974); R. J. LeVeque, Finite Volume Methods for Hyperbolic Problems, Cambridge University Press (2002); and the Artemis research direction of 22 October 2026 and Lanyon proposals of 30 October 2026 in the project."),
);

const doc = new Document({
  creator: "H. P. Alesso", title: "Verifying the Verified: an Artemis-Lanyon audit",
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
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync("../Artemis_Lanyon_Audit_Proposal.docx", buf); console.log("written"); });
