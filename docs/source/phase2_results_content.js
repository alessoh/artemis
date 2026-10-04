// Content for "Artemis Phase 2 Results". Appended to guide_helpers.js at build time.
const children = [];

children.push(
  new Paragraph({ spacing: { before: 1400, after: 120 }, children: [new TextRun({ text: "ARTEMIS", font: HEAD_FONT, size: 22, bold: true, color: TEAL, characterSpacing: 120 })] }),
  new Paragraph({ spacing: { after: 200 }, children: [new TextRun({ text: "Phase 2 Results: The First Lab Run", font: HEAD_FONT, size: 52, bold: true, color: INK })] }),
  new Paragraph({ spacing: { after: 600 }, children: [new TextRun({ text: "What the agents found about earth-abundant solar absorbers, and how well it holds up", font: BODY_FONT, size: 28, italics: true, color: MUTED })] }),
  new Paragraph({
    border: { top: { style: BorderStyle.SINGLE, size: 6, color: NAVY, space: 8 } },
    spacing: { after: 80 }, children: [new TextRun({ text: "Lab session 501042555e83, October 3, 2026  ·  Repository commit ac74125", font: HEAD_FONT, size: 20, color: INK })],
  }),
  new Paragraph({ spacing: { after: 80 }, children: [new TextRun({ text: "Saturday, October 3, 2026", font: HEAD_FONT, size: 20, color: MUTED })] }),
  new Paragraph({ spacing: { before: 1000 }, children: runs("Six AI agents ran the Artemis solar program for about three hours without human help. This document reports what they found, what I checked independently afterwards, and what the result can and cannot claim. Every number comes from the frozen data snapshot, the lab's own records, or analyses I ran and saved in the repository.", { size: 21, color: MUTED }) }),
  new Paragraph({ children: [new PageBreak()] }),
);

children.push(
  H1("1. The answer in brief"),
  P("The lab found a way to rank earth-abundant, non-toxic crystals so that the expensive efficiency calculation reaches excellent solar absorbers much sooner than the usual rules of thumb. Its method puts near-stable materials first and then orders them by an efficiency predicted from cheap DFT properties and composition, using a forest of randomized decision trees trained on the 7,250 materials JARVIS has already assessed."),
  P("On the official held-out test, which the lab was allowed to run once, the method found all four excellent absorbers among 429 candidates after 8 expensive calculations. The best simple rule needed 20, and random search would need about 344. Because four hits is too few to trust on its own, I repeated the comparison afterwards on 20 larger search pools. The lab's method needed fewer calculations than the best simple rule in all 20, with a median of 14.5 calculations against 47.5 to find ten excellent absorbers, and against about 1,160 for random search."),
  Pull("The speed-up over the best simple rule is about three times, and it held in every one of twenty independent trials. The speed-up over random search is between about 40 and 90 times, depending on the size of the search pool."),
  P("The search also taught something physical. Stability matters first. The useful band-gap window for these cheap DFT gaps sits near 0.6 to 0.7 eV rather than at the textbook 1.34 eV, because the OptB88vdW method underestimates gaps, and composition carries information that the gap alone does not."),
);

children.push(
  H1("2. What the lab did"),
  P("The Compiler set up the run, recorded the three reference methods, and then ran seven waves of experiments. In each wave the Planner proposed two or three ideas, Experimenters implemented them in parallel, and the Skeptic re-ran every apparent improvement, read its code for leakage, and tested it again with cross-validation on the training data before the Compiler kept it. Four ideas were kept, each a step up from the last. The lab used 26 of its 60 allowed experiments and stopped by its own rule after three waves brought no kept improvement."),
  table([3000, 1900, 1900, 2560], ["Step kept", "Calculations to 9 practice hits", "Acceleration on practice set", "What changed"], [
    ["Starting rule (gap near 1.34 eV)", "244", "1.7", "Textbook Shockley-Queisser rule"],
    ["Stability-gated rule (reference)", "39", "10.8", "Stable materials first"],
    ["Corrected-gap rule", "21", "20.0", "Gap target moved to the DFT scale"],
    ["Hit classifier", "18", "23.3", "Learned from training materials"],
    ["Efficiency regressor", "15", "28.0", "Predicts SLME instead of yes or no"],
    ["Final model", "13", "32.3", "Randomized trees plus element fractions"],
  ]),
  Caption("Practice set: 465 earth-abundant candidates containing 9 excellent absorbers. Numbers from the lab's ledger."),
  P("The Skeptic earned its place. It rejected the trial with the highest practice score in the whole run (34.95) because cross-validation on the training data showed the gain was an accident of the small practice set, and it rejected two other trials that matched the best score only by adding complexity. That is the behaviour the program asked for, and it is the main reason the final test result can be trusted at all."),
);

children.push(
  H1("3. Checking the lab's work"),
  P("I checked the lab's report against the data rather than taking it on trust. Every result the lab recorded carries the same fingerprints as the frozen scoring script and data snapshot in the repository, so nothing was altered during the run. I re-ran the three reference methods on the practice and test sets and obtained exactly the lab's numbers. I confirmed the counts in the report (158 excellent absorbers among the training materials, 9 in the practice pool, 4 in the test pool, 22,784 never-assessed earth-abundant materials), the gap statistics of the training hits, and every value in the recommendation table."),
  P("Two statements in the report need small corrections. The straight-line fit between the cheap and the accurate band gap uses 6,110 training materials with non-zero gaps, not 6,029; the fitted coefficients the report gives are exactly right. And the report's count of 19 hits among 152 stable materials with a zero gap actually describes materials with gaps up to 0.05 eV; with a gap of exactly zero the count is 18 of 142. Neither changes any conclusion."),
  P("The code of the final model was lost when the session was stopped, because it lived only in the lab's sandbox. I rebuilt it from the report's description and saved it in the repository. The rebuilt model reproduces the lab's practice result exactly, with the ninth hit found at calculation 13 and the same average precision of 0.899, and it reproduces 14 of the lab's 15 recommendations in nearly the same order. That match is strong evidence that the report describes the method completely and that its numbers are honest."),
);

children.push(
  H1("4. Is the speed-up real?"),
  P("The official test had only four excellent absorbers, so the difference between 8 and 20 calculations rests on where a single material landed. To test the claim properly I pooled every earth-abundant material that JARVIS has assessed, 4,409 in all, and split them at random into two halves twenty times. Each time, one half became the search pool and everything else trained the model, and I counted the calculations each method needed to find ten excellent absorbers."),
  Img("../figures/phase2_robustness.png", 600, 275),
  Caption("Each dot is one of the 20 search pools; the black bar marks the median. Data: docs/results/phase2_robustness.csv; code: lab/solar/analysis/robustness.py."),
  table([3600, 1900, 1900, 1960], ["Method", "Median calculations to 10 hits", "Median acceleration vs random", "Median average precision"], [
    ["Random order (expected)", "1,161", "1", "n/a"],
    ["Stability-gated band-gap rule", "47.5", "25.3", "0.239"],
    ["Corrected-gap rule", "26", "40.7", "0.476"],
    ["Lab's final model (rebuilt)", "14.5", "89.1", "0.703"],
  ]),
  Spacer(),
  P("The lab's method beat the stability-gated rule in all 20 pools. The ratio of their calculation counts had a median of 3.35, and in 18 of the 20 pools it was at least 2. The simpler corrected-gap rule the lab discovered also beats the textbook rule clearly, which shows the physical lesson about the gap scale is real and not only a feature of the learned model."),
  P("Two cautions keep this honest. This check was designed and run after the official test, so it is supporting evidence rather than a pre-registered result. And the lab chose its method partly by looking at the practice set, whose materials are now spread through these pools, which could flatter the model slightly; the consistency across all twenty pools, and the Skeptic's earlier cross-validation on training data alone, make a large effect from this unlikely. Acceleration against random search also grows with the size of the pool, so the 43 on the small test pool and the 89 here are not in conflict; the comparison with the best simple rule is the stable number."),
);

children.push(
  H1("5. What the search taught"),
  P("Stability does the first and largest share of the work. Putting near-stable materials first raised the textbook rule's acceleration from about 1.7 to about 11 on the practice set, simply because an excellent absorber must also be stable."),
  P("The second lesson concerns the band-gap scale. Every excellent absorber in the training data with a known accurate (TBmBJ) gap lies between 0.92 and 1.66 eV, with a median of 1.35 eV, close to the ideal Shockley-Queisser value. Their cheap OptB88vdW gaps, however, have a median of only 0.66 eV, because that method systematically underestimates gaps. Among stable training materials, about half of those with cheap gaps between 0.3 and 0.8 eV are excellent absorbers, compared with 13 percent between 1.2 and 1.4 eV and 1 percent above 1.8 eV. Aiming the cheap gap at the textbook 1.34 eV therefore looks in the wrong place."),
  P("The third lesson is that composition matters beyond the gap. The window shifts with the anion: according to the lab's analysis, the median cheap gap of excellent absorbers is about 1.0 eV for halides and about 0.26 eV for chalcogenides. In the training data the excellent absorbers cluster in alkali halides and fluorides and in compounds of antimony, indium, silver, copper and zinc, and the learned model, which sees the elements directly, roughly doubles what any gap rule achieves. Predicting the efficiency itself worked better than predicting a yes or no label, probably because materials just below the 30 percent line still show which direction is better."),
);

children.push(
  H1("6. What to compute next"),
  P("These are the lab's top recommendations among the 22,784 earth-abundant materials that JARVIS has never assessed for solar efficiency. Each is a prediction that needs the expensive calculation; none is yet a discovery. The values are JARVIS's cheap DFT results."),
  table([700, 1500, 1500, 1100, 1300, 3260], ["Rank", "Material", "JARVIS ID", "Cheap gap (eV)", "Above hull (eV/atom)", "Note"], [
    ["1", "Rb2NiF6", "JVASP-90503", "1.606", "0.000", "On the hull; ranked by composition, as its gap is above the usual window"],
    ["2", "SrBeBr2", "JVASP-120881", "1.039", "0.064", "No literature found"],
    ["3", "SmS", "JVASP-78443", "0.000", "0.058", "Metallic at this level; likely false positive"],
    ["4", "CuCl (F-43m)", "JVASP-111073", "0.586", "0.000", "Known experimentally as wide-gap; see below"],
    ["5", "DyS", "JVASP-14566", "0.000", "0.032", "Metallic at this level; likely false positive"],
    ["6", "BaZnCl2", "JVASP-114550", "1.107", "0.020", "No literature found"],
    ["7", "CuCl (Pa-3)", "JVASP-12510", "0.590", "0.011", "As rank 4"],
    ["8", "Na10CaSn12", "JVASP-59094", "0.775", "0.000", "No literature found"],
    ["9", "Na10SrSn12", "JVASP-59095", "0.776", "0.000", "Not searched"],
    ["10", "SrCaGe", "JVASP-10972", "0.471", "0.000", "Only unrelated literature"],
    ["11", "Sr2Ge", "JVASP-9128", "0.388", "0.000", "Not searched"],
    ["12", "CuBr", "JVASP-12504", "0.317", "0.013", "Has gap and band-structure literature"],
    ["13", "Cu2BrCl", "JVASP-100007", "0.423", "0.000", "No literature found"],
    ["14", "BaZnF2", "JVASP-115581", "1.347", "0.000", "No literature found"],
    ["15", "LaS", "JVASP-98069", "0.000", "0.082", "Metallic at this level; likely false positive"],
  ]),
  Caption("The lab's shortlist, values checked against the snapshot. The rebuilt model gives the same list except that BaGeBr (JVASP-66027) replaces LaS at rank 15."),
  P("Twelve of the fifteen are near-stable with a non-zero cheap gap, and they are the natural first calculations. SmS, DyS and LaS have a cheap gap of exactly zero; about one in eight similar training materials is nonetheless an excellent absorber, so they are not impossible, but they belong at the end of the queue. CuCl deserves particular care: experiments describe its common form as a wide-gap material, which would make it a poor absorber despite its rank, and its accurate gap calculation will settle the question quickly. The Materials Project cross-check did not run, because no Materials Project key had been added; with the key, the Scout can report whether each candidate is known experimentally and how stable the Materials Project finds it."),
);

children.push(
  H1("7. What went wrong, and what is fixed"),
  P("Four things went wrong, none of them in the science. The report-saving step read only the first page of the session's history, and the stop command then deleted the session; the report was recovered from the copy streamed to your computer, and both commands are fixed so that stop refuses to delete anything that has not been saved. The final model's code was lost with the sandbox; it is rebuilt and verified, and future runs will include the code and the shortlist in the lead's final message. The never-assessed pool contained four materials listed twice with identical values; the scoring script now keeps one copy, which changes its fingerprint but not any practice or test score. And the Materials Project check was unavailable for lack of a key."),
  P("One design lesson goes into the next version of the program. With only nine practice hits, the rule that a gain below 0.3 in acceleration is noise was far too loose, since a single place in the ranking moves the score by two or three points. The Skeptic's habit of confirming every gain with cross-validation on training data is what protected this run, and the next program will make that the rule rather than the habit."),
);

children.push(
  H1("8. Next steps"),
  P("The most valuable next step costs almost nothing: add the Materials Project key with python scripts/make_secrets.py materials-project, so the next run can cross-check its recommendations against an independent database. Beyond that, I suggest tightening the keep rule as described above and then moving to Phase 3, the public website, where a visitor can watch a run like this one unfold live and read a report like this at the end."),
);

children.push(
  H1("Sources"),
  source("JARVIS-Leaderboard, Choudhary et al., npj Computational Materials 10, 93 (2024)", "https://doi.org/10.1038/s41524-024-01259-w"),
  source("JARVIS, Choudhary et al., npj Computational Materials 6, 173 (2020)", "https://doi.org/10.1038/s41524-020-00440-1"),
  source("JARVIS-DFT 3D release 2021-08-18 (figshare)", "https://doi.org/10.6084/m9.figshare.6815699"),
  source("SLME in JARVIS, Choudhary et al., Chem. Mater. 31, 5900 (2019)", "https://doi.org/10.1021/acs.chemmater.9b02166"),
  source("Crustal abundances, CRC Handbook 97th edition values", "https://en.wikipedia.org/wiki/Abundance_of_elements_in_Earth%27s_crust"),
  source("Pauling electronegativities used in the rebuilt model, pymatgen periodic table data", "https://github.com/materialsproject/pymatgen"),
  source("Wide-gap γ-CuCl, J. Cryst. Growth (2005)", "https://doi.org/10.1016/j.jcrysgro.2005.10.053"),
  source("Lab report, transcript, rebuilt model and robustness data", "https://github.com/alessoh/artemis/tree/main/docs/results"),
);

const doc = new Document({
  creator: "Claude",
  title: "Artemis Phase 2 Results",
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
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "Artemis  ·  Phase 2 Results", font: HEAD_FONT, size: 16, color: MUTED })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: HEAD_FONT, size: 16, color: MUTED })] })] }) },
    children,
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync("Artemis_Phase2_Results.docx", buf);
  console.log("written");
});
