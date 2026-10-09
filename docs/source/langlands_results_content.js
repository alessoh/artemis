// Content for "Artemis Langlands Run: Evaluation". Appended to guide_helpers.js at build time.
const children = [];

children.push(
  new Paragraph({ spacing: { before: 1400, after: 120 }, children: [new TextRun({ text: "ARTEMIS", font: HEAD_FONT, size: 22, bold: true, color: TEAL, characterSpacing: 120 })] }),
  new Paragraph({ spacing: { after: 200 }, children: [new TextRun({ text: "The Langlands Run: An Evaluation", font: HEAD_FONT, size: 48, bold: true, color: INK })] }),
  new Paragraph({ spacing: { after: 600 }, children: [new TextRun({ text: "What the lab found about murmurations, the archimedean sign and local root numbers, how much of it holds up, and what to do next", font: BODY_FONT, size: 28, italics: true, color: MUTED })] }),
  new Paragraph({ border: { top: { style: BorderStyle.SINGLE, size: 6, color: NAVY, space: 8 } }, spacing: { after: 80 },
    children: [new TextRun({ text: "Session 5604bfb2, branch langlands-lab of github.com/alessoh/artemis", font: HEAD_FONT, size: 20, color: INK })] }),
  new Paragraph({ spacing: { after: 80 }, children: [new TextRun({ text: "Thursday, October 8, 2026", font: HEAD_FONT, size: 20, color: MUTED })] }),
  new Paragraph({ children: [new PageBreak()] }),
);

children.push(
  H1("1. The verdict in brief"),
  P("This is the most scientifically interesting of the three Artemis runs, and its results are sound. I rebuilt the lab's final experiment from the code in its report, confirmed that the file is byte for byte the one the lab promoted, and ran the frozen final test again myself. Every number reproduced exactly, from the murmuration correlations to the last digit of each p-value."),
  P("Both pre-registered hypotheses in Part B hold on 209,944 curves with conductors the lab never saw. Within a single conductor, the local root numbers of rank 2 curves really do differ from those of rank 0 curves. The effect is small but certain, and the lab improved on the simple starting rule by a margin whose interval excludes zero. Part A confirmed the predicted flip over Q(√5), which was expected, and also turned up a mismatch in the shape of the pattern that nobody planned for and that deserves a follow-up."),
);

children.push(
  H1("2. Part A: the flip, and a surprise in the shape"),
  P("Over Q the lab reproduced the published murmurations cleanly: the profiles for root number +1 and root number −1 are near-perfect mirror images, with a correlation of −0.98. Over Q(√5), weighting each aₚ by the plus product of the finite local signs gives a profile that correlates positively with the profile over Q, at 0.53 with a 95 percent interval from 0.46 to 0.59. The verdict is consistent with the predicted flip. It survives using PARI's root number for every curve (0.52) and dropping the curves that come from Q (0.53)."),
  P("As the program said in advance, this confirms established theory rather than discovering anything. Deligne's formula and the parity checks in the data build already implied it, so its value is as an explicit, pre-registered demonstration that the archimedean sign shows up inside the murmuration pattern."),
  P("The part that was not planned is more interesting. The two profiles agree for small primes but part company once p passes about 0.6 of the conductor: the pattern over Q turns negative, while the one over Q(√5) stays positive all the way to the end. The same thing appeared in the pilot range. The likeliest explanation is that over Q(√5) the pattern lives on a different scale, perhaps because the natural size of a curve there involves the field's discriminant as well as the conductor norm. The run did not test this, so it is an open question, and a cheap one to test."),
);

children.push(
  H1("3. Part B: local signs do carry rank information"),
  table([3700, 2000, 2100, 1560], ["Score on held-out conductors", "AUC", "95% interval", "z"], [
    ["H_B1: count of split multiplicative primes (fixed before the run)", "0.5217", "0.5165 to 0.5273", "8.6"],
    ["H_B2: the lab's promoted experiment", "0.5426", "0.5356 to 0.5500", "15.1"],
    ["Experiment minus simple rule (paired)", "+0.0209", "+0.0141 to +0.0278", ""],
    ["Positive control: aₚ at good primes below 100", "0.9638", "0.9621 to 0.9654", "160"],
  ]),
  Spacer(),
  P("An AUC of 0.5 would mean the signs say nothing about rank. Both rules sit clearly above it, and the lab's experiment roughly doubles the simple rule's margin. Its test score is slightly higher than its validation score (0.539), so the many looks at the validation set did not inflate it. The positive control puts the size in perspective: almost all of the difference between rank 0 and rank 2 lives in the aₚ at the good primes, and the local signs carry a faint but genuine extra trace."),
  P("The lab's most useful contribution is the description of where that trace lives, and it is a clean piece of mathematics. A −1 sign at a prime of 5 or more points towards rank 2, while a −1 sign at 2 or 3 points towards rank 0. Among additive primes of 5 or more, what matters is whether the sign departs from the Legendre symbol (−1/p). By Rohrlich's formulas such a departure marks the Kodaira types III, III\u2217, IV and IV\u2217. I checked these simple readings on the test conductors afterwards. These checks are post hoc, because the test set was already spent, but the rules were formed beforehand on other data. The one-sentence rule (count the −1 signs at p of 5 or more and subtract those at 2 and 3) scores 0.531 with z = 13, and the departure-from-(−1/p) flag on its own scores 0.518 with z = 9. Both hold up far from where they were found."),
  P("A natural mechanism to propose, though not something the run tested, is the Birch and Swinnerton-Dyer formula: Kodaira type fixes the Tamagawa number at each bad prime, and Tamagawa numbers enter the leading term of the L-function, which is where rank 0 and rank 2 curves differ. I do not know whether this conductor-matched effect has been described before. The Scout found nothing, but its searches were shallow, so novelty should be checked by a specialist before it is claimed."),
);

children.push(
  H1("4. How far the result can be trusted"),
  P("The integrity checks all passed. The harness, runner and data fingerprints match what I committed, and the promoted code passes the static check and uses nothing but its own arguments. I re-ran the test and got identical results. The Skeptic also did real work: it rejected two trials that met the numerical keep rule, one because it scored classes through the set of patterns present at a conductor rather than through their own signs, and one because a placebo split did just as well. The one disclosed deviation, the Planner reading training rows directly in the first wave, was within what its instructions allowed."),
  P("The report has a few weaknesses worth correcting before anything goes public. It calls your memo unpublished, although it is on ResearchGate. It flags its own uncertainty about who wrote the Inventiones paper titled \"Murmurations\"; I believe it is Zubrilina's, but I could not confirm that because the publisher's page refused my request. The interpretive reading in Part B came from exploration on validation data, which the report rightly says should be treated as a hypothesis. My post hoc test checks support it but do not replace a fresh pre-registered test. One more limit: the lab's own commits stayed inside its sandbox, so the record of its intermediate steps exists only in the transcript you saved."),
);

children.push(
  H1("5. What I would do next"),
  P("Three follow-ups would turn this into something publishable. The first is a fresh confirmatory test of the Rohrlich reading, stated in advance as a simple rule, on conductors beyond 500,000, if a pinned version of Cremona's tables or the LMFDB covers them; I have not yet checked which range is available. The second is a mechanism test: adding the Tamagawa numbers from Cremona's tables would show directly whether they explain the sign effect. The third is to repeat Part A with the scale variable changed, for example by including the discriminant of Q(√5), to see whether the two murmuration profiles then line up across the whole range. Each would be a short program in the same lab, with the same frozen judge and the same honesty rules."),
  P("For the hackathon, this run shows Artemis doing exactly what it claims. It took a question from your preprint, confirmed the expected part, found an effect the program did not anticipate, located it in a statable arithmetic rule, and held up under an independent re-run on unseen data."),
);

children.push(
  H1("Sources"),
  source("Lab report, promoted experiment and independent replication", "https://github.com/alessoh/artemis/tree/langlands-lab/docs/results/langlands_run1"),
  source("P. Alesso, Euler's identity and the Langlands program", "https://www.researchgate.net/publication/414016686_Euler_Identity_and_Langlands_Program"),
  source("He, Lee, Oliver and Pozdnyakov, Murmurations of elliptic curves", "https://arxiv.org/abs/2204.10140"),
  source("Zubrilina, Murmurations", "https://arxiv.org/abs/2310.07681"),
  source("Variations on murmurations", "https://arxiv.org/abs/2505.01093"),
  source("J. E. Cremona, elliptic curve data", "https://github.com/JohnCremona/ecdata"),
);

const doc = new Document({
  creator: "Claude", title: "Artemis Langlands Run: Evaluation",
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
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "Artemis  ·  Langlands Run Evaluation", font: HEAD_FONT, size: 16, color: MUTED })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: HEAD_FONT, size: 16, color: MUTED })] })] }) },
    children,
  }],
});
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync("Artemis_Langlands_Results.docx", buf); console.log("written"); });
