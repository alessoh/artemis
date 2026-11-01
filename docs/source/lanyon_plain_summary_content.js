// Content for "The Lanyon Wave-Speed Audit, Explained". Appended to guide_helpers.js at build time.
const children = [];

children.push(
  new Paragraph({ spacing: { before: 600, after: 120 }, children: [new TextRun({ text: "ARTEMIS  LANYON AUDIT", font: HEAD_FONT, size: 22, bold: true, color: TEAL, characterSpacing: 120 })] }),
  new Paragraph({ spacing: { after: 160 }, children: [new TextRun({ text: "Checking the Speed Limits of Verified Physics Code: What We Did, What We Found, and Why It Matters", font: HEAD_FONT, size: 34, bold: true, color: INK })] }),
  new Paragraph({ spacing: { after: 400 }, children: [new TextRun({ text: "A plain-language summary for readers with a college background in science or engineering  ·  H. P. Alesso  ·  1 November 2026", font: BODY_FONT, size: 22, italics: true, color: MUTED })] }),
);

children.push(
  H1("The short version"),
  P("A company called Lanyon AI publishes computer code for simulating physics, such as electromagnetic fields, gases, plasmas and fields around black holes, and attaches mathematical proofs that are meant to make that code trustworthy. We used Artemis, a laboratory in which AI agents do research under strict rules, to check one thing the proofs do not cover: whether each simulation knows how fast its own waves can travel. Out of 72 simulation recipes, 57 get it right. Fifteen do not, and in some of them the code underestimates the fastest wave by a factor of a hundred, or in one family by a factor of tens of thousands. The mistakes are present in the code Lanyon actually ships. All of them slip past the existing proofs for the same reason, and one additional proof, applied across the board, would catch every one."),
);

children.push(
  H1("What Lanyon builds"),
  P("Much of physics is written as conservation laws: equations that say how a quantity such as mass, momentum, energy or magnetic field moves from place to place. To simulate them, a computer chops space into small cells and repeatedly updates each cell by adding what flows in and subtracting what flows out across its walls. The rule for computing that flow at each wall is called the numerical flux, and getting it right is most of the art of writing such a simulation."),
  P("Lanyon's idea is to write each physics problem once, as a short specification file, and generate two things from it automatically: the C code that runs the simulation, and proofs in a language called Lean that a computer checks line by line. Because the code and the proofs come from the same file, they use exactly the same formulas. Lanyon has published 72 such specifications across seven families of equations, with more than two thousand machine-checked theorems. That is a genuinely impressive and useful piece of work, and nothing in this audit questions the idea itself."),
);

children.push(
  H1("Waves, and the speed limit every simulation needs"),
  P("Equations of this kind describe information travelling as waves. In air, a disturbance travels at the speed of sound; in a plasma there are several kinds of magnetic waves, the fastest of which is called the fast magnetosonic wave; in electromagnetism, disturbances travel at the speed of light. Mathematically, these wave speeds are the eigenvalues of a matrix called the flux Jacobian, which describes how the flow at a wall changes when the state of the material changes. If you have taken linear algebra, this is the familiar idea that the eigenvalues of a matrix tell you the natural rates of a system."),
  P("The method Lanyon uses to compute the flow at each wall is a standard one called the local Lax-Friedrichs or Rusanov method. It works by averaging the two sides of the wall and then adding a smoothing term that damps out spurious wiggles. The strength of that smoothing is set by a single number, which we call amax, that is supposed to be at least as large as the fastest wave speed on either side of the wall. A useful picture is a car's shock absorbers: they have to be rated for the hardest bump the road can deliver. If amax is smaller than the fastest real wave, the smoothing is too weak, the method loses the property that guarantees it stays stable, and in practice a simulation can develop oscillations, negative pressures or densities, or simply blow up."),
  P("Each Lanyon specification writes down a list of wave speeds and a formula for amax. Our audit asked two simple questions of every one of them. The first, which we call C1, is whether the listed wave speeds really are the eigenvalues of the flux Jacobian of that same specification. The second, C2, is whether amax is always at least as large as the fastest of those true speeds. Lanyon's proofs check many things, but none of the theorems we examined states either of these."),
);

children.push(
  H1("How we made the test fair"),
  P("It is easy to fool yourself when you go looking for problems, so the audit followed rules borrowed from good experimental science. Before writing any code that could check the specifications, we wrote down, and committed to the project's repository, exactly what would be measured, how the test states would be chosen, four predictions about which specifications would fail, and three hypotheses that the final test would decide. We also generated a secret random number, the seed for the final test, and recorded only its fingerprint in the repository, so that nobody could later claim we had tried many seeds and kept the one we liked. This practice is called pre-registration, and it is how careful medical and psychology studies guard against wishful thinking."),
  P("The checking program, which we call the judge, reads each specification file directly and does its arithmetic exactly, with fractions rather than rounded decimals, so that its verdicts cannot be blamed on rounding error. For each of the 144 combinations of specification and direction, it tested 400 random but physically allowed states, with every number between 0.01 and 10 in size. The judge's files were locked and fingerprinted, so any change to them would have been detected."),
  P("Then a team of six AI agents, built on Anthropic's Claude models, went hunting. Their job was to write a search program that finds the states where amax falls furthest below the fastest real wave. They worked in rounds: one agent planned, others wrote and ran experiments, and a skeptic agent had to approve any improvement before it counted, checking that it did not cheat and that its physics explanation was right. They found that the best strategy was to work out, for each family of equations, where the formula for amax should fail worst, and aim the search there. An agent using a generic optimiser with no such aiming later reached the same score, which tells us the result does not depend on the agents' reasoning being correct. After four more rounds without improvement, the team stopped, as its rules required."),
  P("Finally, the locked search and the census were run once on the secret seed, outside the agents' workspace. As an independent cross-check, we also compiled Lanyon's own C code and tested it at the worst state found for every failing case, to be sure the problems exist in the shipped code and not just in our reading of the specification files. A separate reviewer that had not done the work then checked our reports against the raw output."),
);

children.push(
  H1("What we found"),
  P("The results split cleanly. Fifty-seven of the 72 specifications passed both checks at every state tested. These include all of the ordinary gas dynamics (the compressible and isothermal Euler equations), the electrostatic plasma equations (Vlasov), the advection-diffusion equations, the Burgers equations, and the standard Maxwell equations of electromagnetism. Fifteen specifications, in three families, failed."),
  table(
    [3400, 2400, 3560],
    ["Family (number of specifications)", "Worst amax as a fraction of the fastest real wave", "In plain terms"],
    [
      ["Plasma, ideal MHD (3)", "about 0.5", "smoothing tuned for a wave half as fast as the real one"],
      ["Plasma, ideal MHD with divergence cleaning (3)", "0.000034", "a whole wave left out of the smoothing"],
      ["Electromagnetism with divergence cleaning (3)", "0.10", "a wave allowed to outrun the speed limit tenfold"],
      ["Electromagnetism around black holes (3)", "0.0101", "the speed of light put in the wrong place"],
      ["The same, with divergence cleaning (3)", "0.0101", "the same error, plus a cleaning wave that scales wrongly"],
      ["All other specifications (57)", "1, no shortfall", "correct"],
    ],
  ),
  Caption("Table 1. The fifteen specifications that fail, grouped by family. A value of 1 would mean amax exactly matches the fastest wave; smaller values mean weaker smoothing than the physics requires. The worst values are the smallest found inside the range of states tested."),
  P("In the plasma specifications (ideal magnetohydrodynamics, or MHD, which describes electrically conducting fluids such as the solar wind), the formula for one of the wave speeds, the Alfvén speed, accidentally includes the speed at which the fluid itself is moving, and uses the total magnetic field where the textbook formula uses only the part of the field pointing across the wall. A tell-tale sign is that the listed speeds change if you simply watch the same fluid from a moving car, which physics says should not happen. In the worst case the code's speed limit is about half of the true fastest wave."),
  P("Three of the plasma specifications add a technique called divergence cleaning. Magnetic fields must never have sources or sinks, but numerical errors can create small fake ones, so the method adds an extra field whose job is to carry those errors away as a wave. The specification correctly lists this cleaning wave's speed but then leaves it out of the formula for amax. In a calm, weakly magnetised fluid the other waves are slow, so amax becomes tiny while the cleaning wave still travels fast. The search found states where amax is only 0.000034 of the fastest wave, which is the largest shortfall in the audit and, in our view, the most important finding."),
  P("The electromagnetism specifications with divergence cleaning have a similar issue. They allow the cleaning waves to travel up to the speed of light squared, but set amax equal to the speed of light. When the speed of light is set to 1, as physicists often do by choosing convenient units, this makes no difference; when it is set to 10, the cleaning wave can be ten times faster than the speed limit."),
  P("The black-hole electromagnetism specifications describe fields in curved spacetime using two quantities from general relativity, the lapse, which describes how fast time runs locally, and the shift, which describes how space is dragged along. Here the speed of light appears squared in one half of the equations and not in the other, so the listed wave speeds are correct only when the speed of light is exactly 1. The versions with divergence cleaning have a second error that survives even then: their cleaning waves move at a speed proportional to the square root of the lapse, while the listed speeds are proportional to the lapse itself. Near a black hole, where the lapse becomes small, the square root is much larger than the number, so the cleaning wave outruns amax."),
  P("Every one of these fifteen failures also appears when Lanyon's own compiled C code is tested directly, so they are real properties of the shipped software. The search agents also found no false alarms: they reported no failure in any of the 57 specifications that pass."),
);

children.push(
  H1("Were our predictions right?"),
  P("Only partly, and that is a good sign that the test was honest. We correctly predicted that all six plasma specifications would fail both checks, and that the three electromagnetism specifications with divergence cleaning would fail only the second. But we predicted, without having read the files, that the black-hole versions with cleaning would follow the same milder pattern, and they turned out to fail both checks; and we predicted that the three standard black-hole specifications would pass, and they failed. Because the hypothesis was that all four predictions would hold, it was formally refuted. In other words, the problems turned out to be more widespread than we expected, and the pre-registration forced us to report that plainly rather than quietly adjust our story. The other two hypotheses held completely: the agents' search found every failure at least as severely as the random census did, and Lanyon's C code reproduced every failure."),
);

children.push(
  H1("What this means, and what it does not"),
  P("The audit shows that, in fifteen specifications, the smoothing strength the method relies on can fall below what the physics requires. It does not show that any particular simulation Lanyon or its users have run actually failed. Whether a real simulation goes wrong depends on details such as the size of the time step and the program that drives the simulation, which may set the time step from other quantities and so mask the problem. A small experiment with a simple driver of our own did show the plasma error causing negative pressures in a standard test problem when the fluid was moving, but our driver is not Lanyon's. We also did not rerun Lanyon's Lean proofs, because we could not install their software tools in our environment, and we examined the statements of the relevant theorems rather than all two thousand of them. None of the underlying physics is new; every correct formula used here is in standard textbooks. What is new is finding these specific errors in a code suite presented as formally verified."),
);

children.push(
  H1("Why it matters"),
  P("Formal verification is often described as proving that software is correct, but a proof only guarantees exactly what its theorem says. Lanyon's theorems confirm, for example, that each listed wave speed is a real number, which is true but does not say that it is the right number. The fifteen errors live in that gap, between what was proved and what a user would naturally assume was proved. As AI systems increasingly write scientific code and the proofs that accompany it, independent checks of what the proofs actually cover become important, and this audit is a concrete example of one."),
  P("The good news is that the fix is clear. A single additional theorem in Lanyon's template, stating that amax is at least as large as every true wave speed for every allowed pair of states, would have ruled out all fifteen failures and would protect any future specification against the same mistake. Our tests found that this theorem has counterexamples in exactly fifteen specifications and none in the other 57, so it is the right statement to add."),
);

children.push(
  H1("What happens next"),
  P("We have written privately to Lanyon's founders, Drs. Jonathan Gorard, Ammar Hakim and James Juno, with the results, and promised not to publish anything about them without first sharing it with them and giving them at least thirty days to respond. We have proposed two further stages, pre-registered in the same way. The first would run Lanyon's own code on standard test problems with known answers, with the original and corrected speeds, to find out which of the fifteen errors change real simulation results and by how much. The second would prove the missing theorem in Lean for corrected specifications. All of the code, the pre-registration, the final results and the secret seed are in the Artemis repository, so anyone can rerun the audit and check our work."),
);

children.push(
  H1("A short glossary"),
  table(
    [2600, 6760],
    ["Term", "Meaning"],
    [
      ["Conservation law", "an equation saying a quantity (mass, momentum, energy, field) changes in a region only by what flows across its boundary"],
      ["Flux", "the rate at which a conserved quantity flows across a surface"],
      ["Flux Jacobian", "the matrix of how the flux changes as each variable of the state changes; its eigenvalues are the wave speeds"],
      ["Eigenvalue", "a natural rate of a linear system; here, the speed at which a particular kind of wave travels"],
      ["Rusanov (local Lax-Friedrichs) method", "a simple, robust way to compute the flow between two cells, stable when its smoothing speed amax is at least the fastest wave speed"],
      ["amax", "the smoothing speed the method uses at each cell wall"],
      ["MHD", "magnetohydrodynamics, the physics of electrically conducting fluids such as plasmas"],
      ["Divergence cleaning", "a technique that adds an extra wave to sweep away numerical errors in a magnetic or electric field"],
      ["Lapse and shift", "quantities from general relativity describing how fast time runs and how space is dragged, for example near a black hole"],
      ["Pre-registration", "publishing the hypotheses, predictions and methods before seeing the data, so results cannot be tailored after the fact"],
      ["Lean", "a computer language in which mathematical proofs are written and checked by machine"],
    ],
  ),
);

const doc = new Document({
  creator: "H. P. Alesso", title: "The Lanyon Wave-Speed Audit, Explained",
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
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync("../Artemis_Lanyon_Audit_Explained.docx", buf); console.log("written"); });
