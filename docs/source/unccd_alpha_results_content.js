// Content for "Artemis Project 2: Results". Appended to guide_helpers.js at build time.
const children = [];

children.push(
  new Paragraph({ spacing: { before: 600, after: 120 }, children: [new TextRun({ text: "ARTEMIS  PROJECT 2", font: HEAD_FONT, size: 22, bold: true, color: TEAL, characterSpacing: 120 })] }),
  new Paragraph({ spacing: { after: 160 }, children: [new TextRun({ text: "Choosing UN-CCD's Alpha Without Labels: Results", font: HEAD_FONT, size: 38, bold: true, color: INK })] }),
  new Paragraph({ spacing: { after: 400 }, children: [new TextRun({ text: "The lab's run, the sealed test, and what they mean for Shi, Ceyhan and Billor, arXiv:2501.06268v3", font: BODY_FONT, size: 24, italics: true, color: MUTED })] }),
);

children.push(
  H1("Summary"),
  P("The answer to the question the authors left as future work is yes. A rule that sees only the unlabelled data chose UN-CCD's significance level better than the paper's hand-tuned schedule, on 45 kinds of data the paper never ran and that neither the agents nor we had seen. On those held-out datasets it reached a mean adjusted Rand index (ARI) of 0.928, against 0.863 for the paper's schedule, a gain of 0.065 with a 95 percent interval of 0.036 to 0.098. The first pre-registered hypothesis, H1, which asked only that the rule be no more than 0.02 worse than the schedule, therefore holds with a wide margin. The rule also came within 0.026 of a ceiling that picks the best alpha for each dataset using the true answers."),
  P("The second hypothesis, H2, fails, as the lab itself predicted before the test. H2 asked whether a simple formula in the number of points and the dimension could match the data-driven rule. The lab's best formula, alpha = 240 / (n d²), scored 0.883, which is 0.045 below the rule (interval 0.021 to 0.074 below). The reason is clear from the run: most of the rule's advantage comes from treating differently datasets that have the same size and dimension, which no formula in n and d can do. The formula is still useful: it matched the paper's schedule (0.020 better, interval from 0.009 worse to 0.051 better) while using one constant instead of a table."),
  P("On the five real datasets in the test the picture is different and much less informative. UN-CCD itself does poorly on them whatever alpha is chosen: even the ceiling that uses the true labels averages only 0.27, and the rule (0.220) and the schedule (0.242) are close to each other and to that low ceiling. These five datasets say more about the method than about how alpha is chosen."),
);

children.push(
  H1("What was run"),
  P("The lab ran on 15 October 2026 as Omnigent session d5d40fe5 under the program on the branch unccd-alpha-lab: a lead agent and five specialists (Claude Opus 5.5, with Claude Haiku 4.5 for literature searches) worked on two files, a rule that chooses alpha and the search direction from the data, and a formula that may use only the number of points and the dimension. A frozen harness scored every candidate on 64 validation datasets in the paper's own simulation design, and a candidate was kept only if it beat the current best by at least 0.005 with a paired 95 percent interval above zero and passed the Skeptic's review."),
  P("Over eleven waves the lab ran 15 rule evaluations, 10 formula evaluations and 2 reruns with new seeds, and kept three changes. The rule kept in wave 1 is a null-calibrated silhouette: for each alpha it compares UN-CCD's silhouette with the silhouette that k-means reaches, at the same number of clusters, on five structureless Gaussian samples with the data's mean and covariance, and it chooses the alpha with the largest excess. This raised the validation score from 0.941 to 0.960, against 0.906 for the paper's schedule and 0.968 for the label-using ceiling. The formula went from a fixed 5 percent (0.860) to 1.2 / d² (0.902) and then to 240 / (n d²) (0.9125). After wave 1 the rule was within 0.0046 of the best any ascending-search rule could reach on validation, below the keep bar, and the lab correctly recognised that further rule changes could not be kept on validation. The Skeptic also rejected a formula that passed the numeric test, because its dimension band had been fitted to the validation results after the fact."),
  P("The lab ended by freezing its files and writing its report, which predicted, before the test, that H2 would fail and that the simulations pointed towards H1 holding. Its full report, with every trial, is in the results folder."),
);

children.push(
  H1("The sealed test"),
  P("The test was drawn from a secret seed whose SHA-256 fingerprint was committed in the program before the run; the seed is now published beside the results, and its fingerprint matches. The test holds 45 regimes the paper never ran, in 4, 7 and 15 dimensions, with 30, 300 or 700 points, two, four or six clusters, up to 30 percent background noise and new cluster layouts, two datasets each, and five real datasets the paper did not use. Before running it I rebuilt the lab's two files from its last message and confirmed that their SHA-256 matched the frozen record exactly, as did the harness, the toolkit, the clustering code and the data. The test was run once. A second, independent calculation of every ARI with scikit-learn's own function and a different bootstrap seed reproduced all 90 synthetic scores and both verdicts to four decimals."),
  table(
    [3700, 2300, 3360],
    ["Rule (45 held-out regimes, 90 datasets)", "Mean ARI", "95% interval"],
    [
      ["Lab's rule (null-calibrated silhouette)", "0.928", "0.884 to 0.963"],
      ["Lab's formula, 240 / (n d²)", "0.883", "0.827 to 0.931"],
      ["Paper's hand-tuned schedule", "0.863", "0.800 to 0.917"],
      ["Silhouette maximum (the lab's starting rule)", "0.865", "0.804 to 0.919"],
      ["Fixed alpha of 5%", "0.852", "0.787 to 0.907"],
      ["Fixed alpha of 1% (the paper's stated real-data setting)", "0.834", "0.757 to 0.898"],
      ["Ceiling: best alpha per dataset, ascending (uses labels)", "0.944", "0.907 to 0.975"],
      ["Ceiling: best alpha and direction per dataset (uses labels)", "0.954", "0.919 to 0.981"],
    ],
  ),
  Caption("Table 1. Mean ARI on the held-out synthetic regimes. Noise points are left out of the ARI. Intervals are bootstrap intervals over regimes."),
  table(
    [3100, 2200, 2000, 2060],
    ["Pre-registered comparison", "Difference", "95% interval", "Verdict"],
    [
      ["H1: rule minus paper's schedule", "+0.065", "+0.036 to +0.098", "Holds (needs lower end above -0.02)"],
      ["H2: formula minus rule", "-0.045", "-0.074 to -0.021", "Fails (needs lower end above -0.02)"],
      ["Rule minus silhouette maximum", "+0.063", "+0.035 to +0.097", "reported"],
      ["Rule minus fixed 1%", "+0.094", "+0.047 to +0.147", "reported"],
      ["Rule minus label-using ceiling", "-0.026", "-0.043 to -0.011", "reported"],
      ["Formula minus paper's schedule", "+0.020", "-0.009 to +0.051", "reported"],
    ],
  ),
  Caption("Table 2. Paired differences over the 45 regimes."),
  P("The rule's advantage is broad. It is ahead of the schedule at every dimension (0.935 against 0.891 at d = 4, 0.947 against 0.898 at d = 7, and 0.902 against 0.801 at d = 15), at every size (0.891 against 0.822 at n = 30, 0.930 against 0.864 at 300, 0.963 against 0.903 at 700) and at every noise level. Almost all of the gain is on Gaussian clusters (0.862 against 0.769), where clusters overlap and the choice of alpha matters; on uniform clusters every sensible rule is near perfect (0.997 against 0.962). The largest single gain is in 15 dimensions, where the paper's schedule, extrapolated, does worst."),
);

children.push(
  H1("The real datasets"),
  P("The five real datasets were reported without a pass mark, and they show a limit of the method rather than of the rule. On aggregation the rule scores 0.321 against the schedule's 0.407; on compound it is better (0.400 against 0.366); on glass and jain all rules are within a few hundredths of each other and of a ceiling that is itself low (0.107 and 0.234); on yeast the rules agree with one another (0.091 to 0.094) but sit well below a ceiling of 0.209 that only the descending search reaches. With five datasets and these values, the honest reading is that UN-CCD separates these real clusters poorly at any alpha, so how alpha is chosen hardly matters there."),
  table(
    [2100, 1450, 1450, 1450, 1450, 1460],
    ["Rule", "aggregation", "compound", "glass", "jain", "yeast"],
    [
      ["Lab's rule", "0.321", "0.400", "0.062", "0.224", "0.091"],
      ["Lab's formula", "0.391", "0.366", "0.107", "0.234", "0.091"],
      ["Paper's schedule", "0.407", "0.366", "0.107", "0.234", "0.094"],
      ["Ceiling (labels)", "0.407", "0.400", "0.107", "0.234", "0.209"],
    ],
  ),
  Caption("Table 3. ARI on the five real held-out datasets."),
);

children.push(
  H1("What it means for the paper"),
  P("The paper describes UN-CCD as needing little tuning, while in fact its one parameter was set by hand against the labels, dimension by dimension. This program shows that the claim can be made true. A short, statable, label-free rule, which takes the alpha at which UN-CCD's silhouette most exceeds what the same number of clusters would score on featureless Gaussian data of the same shape, beats the hand-tuned schedule on new kinds of synthetic data, by a margin larger than the schedule's own advantage over a fixed 1 percent, and comes close to what a label-using oracle could do. The idea borrows the calibration of the gap statistic (Tibshirani, Walther and Hastie, 2001) and is not new as a principle; what is new is its application to this method and its pre-registered test against the authors' own setting."),
  P("Two further findings are worth passing to the authors. A formula in n and d alone, however well chosen, cannot match a rule that looks at the data, because most of the gain comes from variation between datasets of the same size and dimension; but the one-constant formula 240 / (n d²), which holds the expected number of chance rejections near 240 / d², matches the paper's whole schedule and extends it to any n and d. And no label-free rule for switching to the descending search helped robustly: its apparent benefit at d = 10 on the paper's design did not survive in the lab's own simulations with randomly placed clusters."),
);

children.push(
  H1("Limits"),
  P("The test regimes were listed publicly in the program, so the agents knew the family they would be tested on and simulated similar data themselves; the datasets were secret, but the test measures transfer to a known family rather than to a surprise. All synthetic data are Gaussian or uniform clusters in the paper's generator family. Alpha was chosen from a grid of 15 values, and the rule picked the smallest value for many datasets, so its preferred alpha may sometimes lie below the grid. The real-data part has only five datasets, on which the method itself is weak. Noise points were left out of the ARI, as the program stated, so the scores measure how well the clusters are recovered, not how well noise is set aside. The lab's records, its ledger and trial files, stayed in its sandbox because pushes were blocked; its final message, the frozen record and its report are kept, and the two final files are reproduced exactly."),
);

children.push(
  H1("Reproducibility record"),
  P("The program, harness and data are on the branch unccd-alpha-lab of github.com/alessoh/artemis. The folder docs/results/unccd_alpha_run1 holds final_test.json with every number above and every dataset's score, frozen.json, the lab's final rule and formula, an excerpt of its final message with its report, the test datasets and the revealed seed. To repeat the test, check out the branch, copy the two final files over lab/unccd_alpha/experiment.py and formula.py, copy frozen.json to runs/unccd_alpha/, rebuild the test with python lab/unccd_alpha/prepare_data.py test --seed-file docs/results/unccd_alpha_run1/test_seed.txt --out lab/unccd_alpha/work/test (the real datasets come from the authors' repository, fetched by lab/unccd/prepare_data.py), precompute its clusterings with harness.py build-cache --split test, and run harness.py final. Fingerprints: harness c19d056bdfff, runner 9be6f26b261c, kit 4bead9b62008, port 6e7fd1ac8b33, data 7f404af31412, rule 2732632753171e12, formula 1dbe3c146c87a5f6."),
  P("The test was run and checked by Claude (Anthropic) at the author's direction; the agents that developed the rule took no part in the test."),
);

children.push(
  H1("Sources"),
  source("Shi, R., Ceyhan, E. and Billor, N. Clustering with Uniformity- and Neighbor-Based Random Geometric Graphs, arXiv:2501.06268v3", "https://arxiv.org/abs/2501.06268"),
  source("Tibshirani, R., Walther, G. and Hastie, T. Estimating the number of clusters in a data set via the gap statistic, JRSS B 63 (2001)", "https://doi.org/10.1111/1467-9868.00293"),
  source("Artemis Project 2 program, harness and results, branch unccd-alpha-lab", "https://github.com/alessoh/artemis/tree/unccd-alpha-lab"),
);

const doc = new Document({
  creator: "H. P. Alesso", title: "Artemis Project 2: Results",
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
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync("../Artemis_UNCCD_Project2_Results.docx", buf); console.log("written"); });
