// Content for "Artemis Lanyon Audit: Results". Appended to guide_helpers.js and the generated rows at build time.
const children = [];
const GH = "https://github.com/alessoh/artemis";
const Code = (text) => new Paragraph({
  spacing: { before: 40, after: 40 }, indent: { left: 360 },
  children: [new TextRun({ text, font: "Consolas", size: 18, color: INK })],
});

children.push(
  new Paragraph({ spacing: { before: 600, after: 120 }, children: [new TextRun({ text: "ARTEMIS  LANYON AUDIT", font: HEAD_FONT, size: 22, bold: true, color: TEAL, characterSpacing: 120 })] }),
  new Paragraph({ spacing: { after: 160 }, children: [new TextRun({ text: "Do Lanyon's Verified Solvers Use the Right Wave Speeds? Results of a Pre-Registered Artemis Run", font: HEAD_FONT, size: 34, bold: true, color: INK })] }),
  new Paragraph({ spacing: { after: 400 }, children: [new TextRun({ text: "H. P. Alesso, with the Artemis laboratory  ·  1 November 2026  ·  branch lanyon-audit, commit 3fc9f50", font: BODY_FONT, size: 22, italics: true, color: MUTED })] }),
);

children.push(
  H1("1. Summary"),
  P("Artemis checked every one of the 72 specifications in Lanyon AI's seven verified-solver repositories against the true wave speeds of its own equations, under rules fixed before any checking code was written. For each specification and direction it asked two questions. Are the wave speeds the specification lists the eigenvalues of the Jacobian of its own flux (check C1)? And is the dissipation speed its local Lax-Friedrichs method uses at least the fastest of those eigenvalues on both sides of an interface (check C2)? The second condition is the one the method's stability rests on."),
  P("Fifteen specifications, in three families, fail C2: the six ideal MHD specifications, the six curved-spacetime Maxwell specifications and the three flat-space hyperbolic Maxwell specifications. Twelve of them, all but the flat-space hyperbolic Maxwell ones, also fail C1. The other 57, covering the standard flat-space Maxwell equations, compressible and isothermal Euler, electrostatic Vlasov, advection-diffusion and Burgers, pass both checks at every one of their 400 sampled interfaces per direction. Every failure is present in the C code Lanyon generates, not only in the specification, and the shortfalls are large. The dissipation speed falls to about one hundredth of the fastest wave in the curved-spacetime specifications, to one half in ideal MHD and to three hundred-thousandths in the divergence-cleaning MHD specifications."),
  P("Of the three pre-registered hypotheses, H1 was refuted because two of its four predictions were wrong: the curved-spacetime specifications fail more widely than predicted. H2, which asks whether the laboratory's own search finds every failure at least as severely as the census, and H3, which asks whether every failure is present in Lanyon's compiled code, both hold on all 30 failing tasks."),
  Pull("The audit's central finding is a missing theorem. Lanyon's theorem statements assert that the listed wave speeds are real numbers, but none that we examined ties them, or the method's dissipation speed, to the eigenvalues of the flux that every specification already defines. None of those statements rules out any failure found here."),
);

children.push(
  H1("2. The question and the rules"),
  P("Each Lanyon specification is a Racket file that pairs a system of conservation laws with a numerical method. It gives the flux in each direction, a list of the characteristic wave speeds, the assumptions under which the state and parameters are admissible, and a solver whose local Lax-Friedrichs (Rusanov) flux uses a dissipation speed, amax, built from those wave speeds. From that one file Lanyon generates a C kernel and Lean proofs. The Rusanov flux is stable only if amax bounds the spectral radius of the flux Jacobian on both sides of each interface, so a dissipation speed below the fastest wave removes the guarantee the method depends on."),
  P("The rules were fixed in a pre-registration committed on 31 October 2026 (commit 59fbe2c), before any code existed that could check the 72 specifications. It defines both checks, a seeded baseline sampler, the sampling box and the census of 400 admissible points per direction, and it states four predictions, written by Claude after reading only some of the specifications. P1 said the six ideal MHD specifications would fail both checks. P2 said the three flat-space hyperbolic Maxwell specifications would pass C1 and fail C2. P3, made with low confidence and without reading the files, said the three curved-spacetime hyperbolic Maxwell specifications would follow the same pattern as P2. P4 said the remaining 60 would pass both checks. It also fixes three hypotheses, all decided once on a secret final seed whose SHA-256 was committed in advance. H1 says the census matches all four predictions. H2 says the laboratory's frozen search finds, for every failing task, a violation at least as severe as the census's worst. H3 says Lanyon's own compiled C kernel reproduces each failure at the census's worst point."),
  P("The judge reads the Racket specifications directly with a reader written for the subset of Racket they use and turns every formula into exact symbolic algebra. Every flux is a rational function and every sample is an exact binary number, so the Jacobian at a sampled point is an exact rational matrix. Its characteristic polynomial is computed over the rationals, and its real roots are isolated exactly, with their multiplicities, before being evaluated to 60 digits. The judge files were fingerprinted with SHA-256 and checked before every evaluation. A separate Claude agent that had not written the code audited them before launch, and the problems it found were fixed and documented in the implementation notes on the branch."),
);

children.push(
  H1("3. What the laboratory did"),
  P("The laboratory is a team of six Omnigent agents running in a Modal sandbox: a Compiler that leads, a Scout for the literature, a Planner, Experimenters, a Skeptic that must approve any claim and a Scribe that writes the report. All ran on Claude Opus 5.5 except the Scout, which ran on Claude Haiku 4.5. Their only lever was one mutable file, experiment.py, which receives one task and must return at most 20 interface points where amax falls furthest below the fastest wave, using a budget of 4,000 checks per task. A run was scored by S, the sum over violating tasks of one minus the smallest confirmed ratio of amax to the spectral radius, and by V, the number of violating tasks. A trial was kept only if it raised S by at least 0.05 without lowering V, held up on two fresh recheck seeds and was approved by the Skeptic."),
  P("Earlier launches stopped when the API key in use ran out of credit, and nothing from them was used. The run that completed set up the snapshot, ran the development census and scored the starting search, which uses only the pre-registered sampler, at S = 17.82 with V = 29. In its first wave it derived, for each failing family, where amax should fall furthest short and aimed its search there. It drew states from physical (primitive) variables in that region and refined the best five by coordinate descent in the logarithm of each value. That search, aimed-primitive-all, scored S = 26.271 with V = 30, held at 26.273 and 26.274 on the two recheck seeds, and was approved by the Skeptic. Four further waves tried simpler annealing, a differential evolution with no physics in it, splitting the left and right states, a different random stream and three budget ablations. None cleared the keep threshold, and the laboratory stopped under its rule of three waves without a kept improvement, having used 15 of its 30 evaluations and 6 of its 10 recheck runs."),
  table(
    [3000, 4060, 1150, 1150],
    ["Trial", "What it tried", "S (eval-1)", "Kept"],
    [
      ["starting search", "pre-registered baseline sampler only", "17.820", "incumbent"],
      ["aimed-primitive-mhd", "aimed MHD draws only, baseline elsewhere", "26.200", "no"],
      ["aimed-primitive-all", "every failing family aimed at its derived weak spot, then log coordinate descent", "26.271", "yes"],
      ["primitive-neldermead", "broad primitive draws with Nelder-Mead, no target region", "23.647", "no"],
      ["minimal-corners", "same corners, simpler random annealing, about half the code", "26.278", "no (gain 0.006)"],
      ["blind-de", "differential evolution with no physics, MHD from primitives", "26.278", "no (gain 0.007)"],
      ["budget-ablation-100", "the kept search capped at 100 checks per task", "26.187", "no (ablation)"],
      ["lr-split-de", "left and right states optimised separately", "26.272", "no"],
    ],
  ),
  Caption("Table 1. Selected trials from the laboratory's ledger, scored on evaluation seed eval-1. The full ledger has 15 evaluations and is quoted in the laboratory's own report."),
  P("Two features of this history matter for the science. An optimiser with no target regions, a differential evolution that used physics only to draw MHD states from physical variables, reached the same corners and the same score as the derived search on all 30 tasks, so the result does not depend on the laboratory's reasoning about where to look. And by the laboratory's derivation, which Section 5 checks, the largest S attainable inside the sampling box is about 26.279, so the kept search reaches essentially the limit of what the box allows. A search capped at 100 checks per task already gets within 0.1 of it."),
);

children.push(
  H1("4. Results on the final seed"),
  P("The final step was run once, on 1 November 2026 from 02:08 to 02:14 UTC, in a fresh clone of the branch outside the laboratory's sandbox. The laboratory had frozen its search at a sandbox commit that cannot be pushed, so experiment.py was rebuilt from the full text in the laboratory's closing report. Its SHA-256 matched the frozen record, the fingerprints of all seven judge files matched, the seed matched the hash committed in the pre-registration, and Lanyon's seven repositories were verified file by file at their pinned commits. The C-kernel preflight compiled Lanyon's generated driver for all 144 tasks before any result was produced."),
  H2("4.1 H1: the census against the predictions"),
  table(
    [800, 3460, 3300, 1800],
    ["", "Specifications", "Prediction", "Outcome"],
    [
      ["P1", "6 ideal MHD", "fail C1 and C2", "confirmed, 6 of 6"],
      ["P2", "3 hyperbolic Maxwell", "pass C1, fail C2", "confirmed, 3 of 3"],
      ["P3", "3 curved-spacetime hyperbolic Maxwell", "pass C1, fail C2", "refuted, 0 of 3 (they also fail C1)"],
      ["P4", "the other 60", "pass C1 and C2", "refuted, 57 of 60 (the 3 curved-spacetime Maxwell fail both)"],
    ],
  ),
  Caption("Table 2. The pre-registered predictions and the census on the final seed. H1 required all four to hold, so H1 is refuted. Twelve specifications fail C1 and fifteen fail C2, the same set as on the development seed."),
  P("The two wrong predictions are both on the side of underestimating the problem. P3 was flagged in advance as a guess about files that had not been read. P4 placed the standard curved-spacetime Maxwell specifications among those expected to pass, and they fail because their wave speeds are right only in units where the speed of light is one (Section 5)."),
  H2("4.2 H2 and H3: the laboratory's search and Lanyon's compiled code"),
  table(
    [2500, 900, 1300, 1300, 1260, 2100],
    ["Specification", "C1", "Census smallest ratio", "Search smallest ratio", "H2 and H3 tasks", "C2 with c = 1 (exploratory)"],
    FAIL_ROWS,
  ),
  Caption("Table 3. The fifteen specifications that fail C2 on the final seed. A ratio is amax divided by the spectral radius at the worst point found, so smaller is worse and 1 means no shortfall. Each specification has one task per direction, 30 in all. H2 and H3 hold on every task. The last column is the exploratory census with c fixed to 1; specifications without a parameter c are marked not applicable."),
  P("H2 holds on all 30 tasks: on the final seed the frozen search found a smaller confirmed ratio than the census on every one, scoring S = 26.273 with V = 30. It also found no violation in any of the 114 tasks that pass, so it raised no false alarms. The gain over the census is largest where the census is weakest. In ideal MHD the census draws conserved variables and so rarely produces a state with positive pressure (eight MHD tasks reached fewer than 400 admissible points), while the search draws physical variables directly."),
  P("H3 holds on all 30 tasks. At each census worst point, the dissipation speed computed by Lanyon's compiled C kernel equalled the specification's to within the pre-registered relative tolerance of 1e-9. The spectral radius of a central finite-difference Jacobian of the C flux exceeded that speed in every case, and matched the exact value from the specification closely. For gr_maxwell_1d, for instance, the C kernel's amax is 9.85 while the finite-difference spectral radius of its flux is 735.64, against an exact 735.64. The failures are therefore in the code Lanyon ships, established independently of the symbolic route."),
);

children.push(
  H1("5. Why each family fails"),
  P("Each failure has a short explanation that follows from the specification's own flux. After the run, an independent reviewer checked each derivation against the specification files, and the curved-spacetime ones with exact algebra."),
  P("**Ideal MHD.** The specifications build their Alfvén speed as vA = u − |B|/√ρ, so the flow velocity enters it, and the fast and slow speeds use the total field where the standard formula uses the normal component. The listed speeds are therefore not the eigenvalues of the flux at any state tested, which is the C1 failure. The dissipation speed is worst when the normal flow equals |B|/√ρ at low pressure. There the listed speeds give amax of about |B|/√ρ, while the true fast wave travels at the flow speed plus a fast speed at least as large, so the ratio approaches one half. The search reached 0.5004."),
  P("**Ideal MHD with divergence cleaning.** These specifications carry the same Alfvén error and add a cleaning field ψ whose waves travel at ±χ. They list ±χ among the wave speeds but leave them out of amax, which uses only the fast speeds. In a fluid nearly at rest with a weak field and little internal energy, amax shrinks with the sound and Alfvén speeds while the cleaning wave keeps travelling at χ. Inside the sampling box the search pushed the ratio to 3.4e-5. The Skeptic noted that the worst points use an adiabatic index very close to one, which the specification's assumption that it exceeds one allows."),
  P("**Flat-space hyperbolic Maxwell.** The cleaning fields travel at cχ and cγ, and the specifications allow χ and γ up to c, so the cleaning waves can reach c². The dissipation speed is |c|, so the ratio falls to 1/c, which is 0.1 at the box's largest c of 10. The listed speeds are correct, so these specifications pass C1. With c = 1, χ and γ cannot exceed one and the problem disappears."),
  P("**Curved-spacetime Maxwell.** The flux multiplies the magnetic constitutive term by c² but not the electric one, so the shift β enters the two halves of each transverse pair differently. Exact algebra on the specification's flux gives the transverse eigenvalues in direction x as −(c² + 1)β/2 ± √((c² − 1)²β²/4 + c²α²), where α is the lapse. The specification lists −β ± αc, which agrees with this at every state only when c = 1; for other values of c it agrees only where the normal shift is zero. For a small lapse, large c and large shift, the fastest true wave approaches c²|β| while amax is αc + |β|, and the ratio falls to about 0.0101 at the corner of the box. The search reached 0.01010 on every task."),
  P("**Curved-spacetime hyperbolic Maxwell.** These carry the same error and add cleaning waves. When the transverse shift is zero, the (D, φ) and (B, ψ) blocks of the Jacobian give cleaning speeds of cχ√α and cγ√α, which scale with the square root of the lapse. The specification lists them as (αc − β)χ and (αc − β)γ, which scale with the lapse itself, and leaves them out of amax. With c = 1, α = 1/4, χ = γ = 1 and no shift, for example, the exact eigenvalues are ±1/2 for cleaning and ±1/4 for light, while amax is 1/4. This is why these three specifications still fail when c is fixed to one."),
);

children.push(
  H1("6. Units with c = 1 (exploratory)"),
  P("Lanyon may intend units in which the speed of light is one, so the final step also ran the census with c fixed to 1 for the twelve specifications that have the parameter. This analysis was announced in the implementation notes before the run but is not part of the pre-registration, and it is reported as exploratory. With c = 1 the flat-space hyperbolic Maxwell and the standard curved-spacetime Maxwell specifications pass both checks, so those failures matter only outside the intended units. The three curved-spacetime hyperbolic Maxwell specifications still fail both checks, with smallest ratios between 0.84 and 0.91 in the census. The six ideal MHD specifications have no parameter c, and their failures do not depend on units at all."),
  P("The findings that do not depend on units are therefore the ideal MHD wave speeds and the curved-spacetime divergence cleaning, which fail even with c = 1, and the omission of the cleaning speed from amax in the MHD specifications with divergence cleaning, which makes the dissipation speed arbitrarily small relative to the fastest wave."),
);

children.push(
  H1("7. What is new and what is not"),
  P("The physics is not new. The ideal MHD eigenvalues are textbook results (Brio and Wu 1988; Roe and Balsara 1996). The extra waves of hyperbolic divergence cleaning travel at the cleaning speed and must be included in a Rusanov dissipation speed, for Maxwell's equations (Munz and co-authors 2000) and for MHD (Dedner and co-authors 2002). The 3+1 constitutive relations in the curved-spacetime specifications are those used for black-hole magnetospheres (Komissarov 2004; McKinney 2006), and the condition that a Rusanov speed bound the spectral radius is standard (Rusanov 1961; LeVeque 2002; Toro 2009)."),
  P("What is new is the audit: the finding that 15 of the 72 specifications in a formally verified solver suite, at the pinned commits, use dissipation speeds that fall below the fastest wave of their own equations, that 12 list wave speeds that are not eigenvalues of their own flux, and that the theorem statements we examined do not rule these defects out, while they are present in the generated C code. The finding points to one remedy that would close the gap for every family at once: a theorem in Lanyon's template stating that, for every admissible pair of states, amax is at least the magnitude of every eigenvalue of the flux Jacobian. None of the sources available to us reports these defects, but the literature search was limited and this should not be taken as a claim of priority until it has been checked properly."),
);

children.push(
  H1("8. Limits and deviations"),
  P("C1 and C2 are pointwise checks on the flux Jacobian at interface states. A violation shows that the dissipation speed falls below the fastest characteristic speed at that state. It does not show that a particular simulation becomes unstable, or by how much, since that depends on the time step, reconstruction and time integrator that a driver uses, and Lanyon's own drivers may set the time step or dissipation from other speeds. Every ratio in the tables was found at a point inside the pre-registered sampling box, where each value is zero or has magnitude between 0.01 and 10, and the limiting ratios quoted are limits within that box. Lanyon's Lean proofs were not rerun, because the Lean and Mathlib toolchain could not be fetched into our environment, so this audit says nothing about whether those proofs check; it says what they leave unstated."),
  P("Several departures from the letter of the pre-registration are recorded in the implementation notes and repeated here. Eigenvalues were confirmed exactly rather than with 50-digit QR iteration, which failed to converge on the curved-spacetime Jacobians. Points that are admissible in double precision but have complex eigenvalues exactly are skipped and counted rather than stopping the census. The sampling box is enforced in scoring the search so that the H2 comparison is like for like, a refinement the pre-registration's H2 text does not mention. The c = 1 census is exploratory. And the frozen search was rebuilt from the laboratory's printed report rather than fetched from its commit, with its hash verified. The development census and the starting search's score were seen by the humans before launch, so H1 was in practice expected to fail, and the laboratory's contribution is H2 and the explanations. The laboratory's Scout returned some literature items with attribution errors, including a reported 2026 paper that could not be verified, and none of them is cited here."),
);

children.push(
  H1("9. How to reproduce"),
  P("Everything needed is on the lanyon-audit branch, including the final seed, which the pre-registration allows into the repository once the final run is done. The judge fetches Lanyon's repositories at the pinned commits and refuses to run if any file differs from the manifest. Because the final step refuses to run twice in the same folder, a rerun needs a fresh clone, Python with numpy, scipy, sympy and mpmath, Git and gcc, and takes a few minutes."),
  Code("git clone --branch lanyon-audit https://github.com/alessoh/artemis && cd artemis"),
  Code("pip install -r requirements-lanyon-audit.txt"),
  Code("python lab/lanyon_audit/prepare_data.py"),
  Code("mkdir -p runs/lanyon_audit && cp lab/lanyon_audit/results/frozen.json runs/lanyon_audit/"),
  Code("cp lab/lanyon_audit/results/final_seed.txt lab/lanyon_audit/work/secret_final_seed.txt"),
  Code("python lab/lanyon_audit/harness.py final"),
  P("The output is runs/lanyon_audit/final.json, which can be compared with the committed lab/lanyon_audit/results/final.json."),
);

children.push(
  H1("Sources"),
  source("Lanyon AI repositories (MaxwellEquations 801558f, GeneralRelativisticMaxwell b13da44, CompressibleEuler a736aa5, IdealMHD beeff1a, ElectrostaticVlasov f43676e, AdvectionDiffusion 71d2724, BurgersEquation dd9b081)", "https://github.com/lanyonai"),
  source("Artemis, branch lanyon-audit: pre-registration, judge, frozen search and final results", `${GH}/tree/lanyon-audit/lab/lanyon_audit`),
  source("M. Brio and C. C. Wu, An upwind differencing scheme for the equations of ideal magnetohydrodynamics, J. Comput. Phys. 75 (1988) 400-422", "https://doi.org/10.1016/0021-9991(88)90120-9"),
  source("P. L. Roe and D. S. Balsara, Notes on the eigensystem of magnetohydrodynamics, SIAM J. Appl. Math. 56 (1996) 57-67", "https://doi.org/10.1137/S003613999427084X"),
  source("C.-D. Munz, P. Omnes, R. Schneider, E. Sonnendrücker and U. Voß, Divergence correction techniques for Maxwell solvers based on a hyperbolic model, J. Comput. Phys. 161 (2000) 484-511", "https://doi.org/10.1006/jcph.2000.6507"),
  source("A. Dedner, F. Kemm, D. Kröner, C.-D. Munz, T. Schnitzer and M. Wesenberg, Hyperbolic divergence cleaning for the MHD equations, J. Comput. Phys. 175 (2002) 645-673", "https://doi.org/10.1006/jcph.2001.6961"),
  source("S. S. Komissarov, Electrodynamics of black hole magnetospheres, MNRAS 350 (2004) 427-448", "https://doi.org/10.1111/j.1365-2966.2004.07598.x"),
  source("J. C. McKinney, General relativistic force-free electrodynamics: a new code and applications to black hole magnetospheres, MNRAS 367 (2006) 1797-1807", "https://doi.org/10.1111/j.1365-2966.2006.10087.x"),
  source("R. J. LeVeque, Finite Volume Methods for Hyperbolic Problems, Cambridge University Press, 2002", "https://doi.org/10.1017/CBO9780511791253"),
  source("E. F. Toro, Riemann Solvers and Numerical Methods for Fluid Dynamics, 3rd ed., Springer, 2009", "https://doi.org/10.1007/b79761"),
  P("V. V. Rusanov, The calculation of the interaction of non-stationary shock waves with barriers, Zh. Vychisl. Mat. Mat. Fiz. 1 (1961) 267-279."),
);

const doc = new Document({
  creator: "H. P. Alesso", title: "Artemis Lanyon Audit: Results",
  styles: {
    default: { document: { run: { font: BODY_FONT, size: 22, color: INK } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: HEAD_FONT, color: NAVY },
        paragraph: { spacing: { before: 360, after: 160 }, outlineLevel: 0, keepNext: true } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 23, bold: true, font: HEAD_FONT, color: TEAL },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1, keepNext: true } },
    ],
  },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: HEAD_FONT, size: 16, color: MUTED })] })] }) },
    children,
  }],
});
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync("../Artemis_Lanyon_Audit_Results.docx", buf); console.log("written"); });
