// Content for "A Note for the Authors of UN-CCD" (short, collegial version).
// Appended to guide_helpers.js at build time.
const children = [];
const GH = "https://github.com/alessoh/artemis/blob";

children.push(
  new Paragraph({ spacing: { before: 200, after: 60 }, children: [new TextRun({ text: "H. P. Alesso, AI HIVE", font: HEAD_FONT, size: 22, bold: true, color: NAVY })] }),
  new Paragraph({ spacing: { after: 360 }, border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: TEAL, space: 8 } }, children: [new TextRun({ text: "15 October 2026", font: HEAD_FONT, size: 20, color: MUTED })] }),
  new Paragraph({ spacing: { after: 240 }, children: [new TextRun({ text: "UN-CCD as a test case for Artemis: a reproduction, and a label-free choice of alpha", font: HEAD_FONT, size: 26, bold: true, color: INK })] }),
);

children.push(
  P("Dear Dr. Shi, Dr. Ceyhan and Dr. Billor,"),
  P("I read your paper, \"Clustering with Uniformity- and Neighbor-Based Random Geometric Graphs,\" with real interest, and I wanted to share some work it inspired. I have been building Artemis, a research laboratory in which teams of AI agents carry out studies under rules meant to keep them honest: they can change only their own code, a frozen program does the scoring, the hypotheses are fixed in advance, and the final answer is tested once on data nobody has seen. Your paper became our first test case on published work by others, in large part because you made it so easy to check. Publishing your code, your data loaders and even your random seed is generous, and it made everything below possible."),
);

children.push(
  H1("Reproducing your results"),
  P("We first reran your R code on the paper's simulation settings. Because your drivers use a single seeded random stream, we could cluster exactly the datasets you clustered, and the results reproduced very well: fourteen of the fifteen cells we checked agree, including the headline case of three uniform clusters in 20 dimensions (0.909 against your 0.921). The one exception is in your favour, since the code does better than the paper reports on five uniform clusters in 20 dimensions."),
  P("On the real datasets of Table 13 we noticed a few things we could not quite square, and I suspect you will have simple explanations for them. The real-data driver uses a different alpha for each dataset, between 5 and 20 percent, where the text mentions 1 percent; results on a few datasets change with the order of the rows; and the Louvain entry for the asymmetric data seems to match the aggregation row of your captured output. We have written these up carefully, along with a short list of smaller differences between the code and the text, and I would be glad to send them if they would be useful."),
);

children.push(
  H1("Choosing alpha without labels"),
  P("The part I most wanted to tell you about takes up the fourth item in your list of future work, automating the choice of the significance level alpha. We asked the Artemis agents to find a rule that picks alpha from the unlabelled data alone. The rule they settled on is simple: for each candidate alpha it compares UN-CCD's silhouette with what k-means achieves, at the same number of clusters, on structureless Gaussian data of the same mean and covariance, and keeps the alpha with the largest margin. The idea of calibrating against a featureless reference is borrowed from the gap statistic of Tibshirani, Walther and Hastie; what is new is applying it to UN-CCD."),
  P("We tested it once, on 90 simulated datasets of kinds the paper did not run (4, 7 and 15 dimensions, varied sizes, cluster counts and noise levels), generated from a secret seed after the rule was frozen. The rule reached a mean adjusted Rand index of 0.928, against 0.863 for your hand-tuned schedule, and came close to the 0.954 an oracle reaches by choosing alpha with the true labels. The agents also found that a one-constant formula, alpha = 240 / (n d²), does about as well as the schedule and extends it to any sample size and dimension. One honest caveat: on five real benchmark datasets we added (aggregation, compound, glass, jain and yeast) UN-CCD found the clusters hard at any alpha, so the result speaks mainly to the simulation setting. Even so, I think it supports your description of the method as largely parameter-free, and it may be a useful step toward that future-work item."),
);

children.push(
  H1("Where to go from here"),
  P("Everything is public, including the code, the frozen rule, the test data and the revealed seed, so the results can be checked independently. We also have a Python port of UN-CCD that reproduces your R code exactly on 60 test cases and runs several times faster. I would be very happy to send more detail on any part of this, to contribute any of it to your repository, or simply to talk it over. Most of all, I would value your view of whether the alpha rule is useful to you, and whether there is anything we have misunderstood."),
  P("Thank you again for a clear and stimulating paper. I look forward to hearing from you."),
  new Paragraph({ spacing: { before: 120, after: 40 }, children: [new TextRun({ text: "With best regards," })] }),
  new Paragraph({ spacing: { after: 360 }, children: [new TextRun({ text: "H. P. Alesso" })] }),
);

children.push(
  H1("Further information"),
  source("Full reproduction report, with every result and code reference", `${GH}/unccd-repro/docs/Artemis_UNCCD_Reproduction_Report.docx`),
  source("Full report on the alpha study and its sealed test", `${GH}/unccd-alpha-lab/docs/Artemis_UNCCD_Project2_Results.docx`),
  source("The label-free alpha rule, as frozen before the test", `${GH}/unccd-alpha-lab/docs/results/unccd_alpha_run1/experiment_final.py`),
  source("Reproduction code and results", "https://github.com/alessoh/artemis/tree/unccd-repro"),
  source("Alpha study code, Python port of UN-CCD, test data and seed", "https://github.com/alessoh/artemis/tree/unccd-alpha-lab"),
  source("Your paper, arXiv:2501.06268v3", "https://arxiv.org/abs/2501.06268"),
  source("Tibshirani, Walther and Hastie, the gap statistic (2001)", "https://doi.org/10.1111/1467-9868.00293"),
);

const doc = new Document({
  creator: "H. P. Alesso", title: "UN-CCD as a test case for Artemis",
  styles: {
    default: { document: { run: { font: BODY_FONT, size: 22, color: INK } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: HEAD_FONT, color: NAVY },
        paragraph: { spacing: { before: 280, after: 120 }, outlineLevel: 0, keepNext: true } },
    ],
  },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: HEAD_FONT, size: 16, color: MUTED })] })] }) },
    children,
  }],
});
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync("../Artemis_UNCCD_Note_to_Authors.docx", buf); console.log("written"); });
