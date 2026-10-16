// Content for "A Note for the Authors of UN-CCD". Appended to guide_helpers.js at build time.
const children = [];

children.push(
  new Paragraph({ spacing: { before: 600, after: 120 }, children: [new TextRun({ text: "A NOTE FOR THE AUTHORS", font: HEAD_FONT, size: 22, bold: true, color: TEAL, characterSpacing: 120 })] }),
  new Paragraph({ spacing: { after: 160 }, children: [new TextRun({ text: "UN-CCD Reproduced, and Its Alpha Chosen Without Labels", font: HEAD_FONT, size: 38, bold: true, color: INK })] }),
  new Paragraph({ spacing: { after: 120 }, children: [new TextRun({ text: "An independent study of Shi, Ceyhan and Billor, \"Clustering with Uniformity- and Neighbor-Based Random Geometric Graphs\", arXiv:2501.06268v3, carried out as a test case for the Artemis AI research laboratory", font: BODY_FONT, size: 24, italics: true, color: MUTED })] }),
  new Paragraph({ spacing: { after: 400 }, children: [new TextRun({ text: "H. P. Alesso, AI HIVE  ·  15 October 2026", font: HEAD_FONT, size: 20, color: MUTED })] }),
);

children.push(
  H1("Why we are writing"),
  P("Dear Dr. Shi, Dr. Ceyhan and Dr. Billor,"),
  P("This note accompanies my email and sets out, as plainly as I can, what we did with your paper and what we found. I began by writing a review of your paper, and from that review grew two pieces of work. The first was an independent reproduction of your published results from your own public code. The second took up a question you leave open in your list of directions for future work, namely how to choose UN-CCD's significance level alpha automatically, without the true labels. We used both as a test case for Artemis, a laboratory in which AI agents carry out research under rules designed to keep them honest. The results of the second project are, I think, genuinely interesting for your method, and the first raises a few questions that only you can answer."),
  P("I want to say at the outset that your decision to publish your code, your data loaders and your simulation drivers, down to the random seed, is what made any of this possible. Very few methods papers can be checked this thoroughly, and yours largely stands up to the check."),
);

children.push(
  H1("Artemis, in brief"),
  P("Artemis follows the \"autoresearch\" pattern described by Andrej Karpathy. A team of AI agents (Anthropic's Claude models in this work) is given a research question, a single file it is allowed to change, and a frozen scoring program it cannot touch. The agents propose an idea, write it into their file, have it scored, and keep it only if it beats the current best by a margin that a paired bootstrap confirms is not chance. A separate agent acts as a skeptic and can veto a change that looks like overfitting. The hypotheses and pass marks are written down before the work starts. When the agents finish, their final files are frozen and fingerprinted, and only then are they scored, once, on test data drawn from a secret random seed whose fingerprint was published in advance. A second, independent calculation then checks every number."),
  P("The point of this design is that nobody, human or machine, can tune the answer to the test. Your paper was an attractive test case because it is a careful, recent methods paper with public code, a clear quantitative standard (the adjusted Rand index, or ARI, which is 1 for a perfect recovery of the true clusters and about 0 for a random one), and an open question stated by the authors themselves."),
);

children.push(
  H1("Part one: reproducing the paper"),
  P("We cloned your repository at commit 9bc8032 and ran your R code on the paper's simulation settings and on the seven datasets of Table 13. The Monte Carlo null tables for the nearest-neighbour statistics are not in the repository, so we rebuilt them with 10,000 iterations, as yours use, and checked our generator against yours in 2 and 10 dimensions. Because your drivers draw every dataset from a single random-number stream seeded with 2024, we were able to replay that stream and cluster exactly the datasets you clustered, repetition by repetition."),
  P("The central simulation evidence holds up well. Of the fifteen simulation cells we checked, fourteen reproduce. That includes the headline comparison of three uniform clusters in 20 dimensions with 200 points, where we obtain an ARI of 0.909 (95 percent interval 0.894 to 0.924) against your published 0.921. The one cell that does not reproduce errs in your favour: for five uniform clusters in 20 dimensions the code gives 0.916, far better than the published 0.750. Your captured log for that cell does show 0.750, so it came from some run of your code, but not, it seems, from the code and settings now in the repository. A run near a 1 percent level would explain the ARI, though not entirely the success rate."),
  P("The real-data results are more qualified. With the settings in your real-data driver and the rows in their stored order, five of the seven UN-CCD results in Table 13 reproduce, most to the third decimal. Those driver settings, however, are not the ones the paper describes. Section 5 says alpha was 1 percent for every dataset, while the driver uses 10 percent for iris, 5 percent for seeds, user knowledge and wholesale, 20 percent for asymmetric and 15 percent for R15 and D31, and switches seeds to the descending scan. Run as the paper describes it, UN-CCD gives quite different numbers, worse on R15, D31 and seeds, and much better on the asymmetric data, where it finds all five clusters (ARI 0.924). Results also depend on the order of the rows: on seeds the ARI ranges from 0.35 to 0.77 across 100 shuffles, and on wholesale the number of clusters ranges from 2 to 54. The covering-ball radii themselves do not depend on order, so the sensitivity seems to enter where the greedy steps break ties by taking the first of several equal candidates."),
  P("Reading the code beside the paper, we found thirteen places where the two differ, all listed with file and line numbers in the reproduction report that accompanies this note. Most are the ordinary residue of a long project. A few seem worth your attention. The Louvain entry for the asymmetric data in Table 13 (ARI 0.805, 8 clusters) matches, in all three numbers, the aggregation row of your own captured Louvain output, while the asymmetric row there gives 0.561 with 3 clusters, which is what we find. The test in UN_CCD.R rejects when either statistic falls below its alpha quantile, which is more liberal than the Holm step-down procedure the paper describes. The simulation drivers call UNMCCD_outlier, which the file they load does not define. The Gaussian drivers place cluster centres at 9 rather than 6 and scale the covariance slightly differently from the text. And no driver for the noise study of Section 4.3 is in the repository. None of these overturns your main conclusion."),
);

children.push(
  H1("Part two: choosing alpha without labels"),
  P("UN-CCD has essentially one parameter that matters, the level alpha of the spatial randomness test that decides how far each covering ball may grow. In the paper it is set by hand for each dimension, from 15 percent in two dimensions down to 0.1 percent in twenty, and as we understand it these values were reached by trial and error against the true labels. You list automating that choice as future work. We asked the Artemis agents to find a rule that chooses alpha, and the search direction, from the unlabelled data alone."),
  P("To make the work fast enough for the agents, we first ported UN-CCD from your R code to Python line by line, keeping R's tie-breaking. On 60 test cases, six of the real datasets of Table 13 at two settings each and 48 simulated datasets in two to twenty dimensions, the port gives exactly the same radii, dominating balls and clusters as your code, and runs three to ten times faster. The agents worked on development and validation datasets drawn from your own simulation design. Before the run we fixed two hypotheses. H1 said the agents' final rule would be no worse than your hand-tuned schedule by more than 0.02 in mean ARI on held-out data. H2 said a closed-form formula in the number of points n and the dimension d alone, with at most three constants, would match the agents' rule in the same sense."),
  P("The sealed test was deliberately different from the paper's design: 45 kinds of data the paper never ran, in 4, 7 and 15 dimensions, with 30, 300 or 700 points, two, four or six clusters, up to 30 percent background noise and new cluster layouts, two datasets each, together with five real benchmark datasets the paper did not use. Table 1 gives the results on the 90 synthetic test datasets."),
  table(
    [5000, 1800, 2560],
    ["How alpha was chosen (90 held-out datasets)", "Mean ARI", "95% interval"],
    [
      ["The agents' rule, label-free", "0.928", "0.884 to 0.963"],
      ["The agents' formula, alpha = 240 / (n d²)", "0.883", "0.827 to 0.931"],
      ["The paper's hand-tuned schedule", "0.863", "0.800 to 0.917"],
      ["Maximum silhouette (the agents' starting point)", "0.865", "0.804 to 0.919"],
      ["Fixed alpha of 1 percent", "0.834", "0.757 to 0.898"],
      ["Best alpha per dataset, chosen using the true labels", "0.954", "0.919 to 0.981"],
    ],
  ),
  Caption("Table 1. UN-CCD on the sealed test, scored once. Noise points are left out of the ARI. Intervals are bootstrap intervals over the 45 regimes. The last row is an oracle that no real rule can match, shown to mark the ceiling."),
  P("H1 holds with a wide margin. The agents' rule beat your schedule by 0.065 (95 percent interval 0.036 to 0.098), where the hypothesis required only that it lose by no more than 0.02. It came within 0.026 of the oracle that picks the best alpha for each dataset by looking at the answers. Its advantage is broad: it was ahead at every dimension, every sample size and every noise level, with the largest gain in 15 dimensions (0.902 against 0.801), where your schedule has to be extrapolated. Almost all of the gain is on Gaussian clusters, which overlap and where the choice of alpha matters most. On uniform clusters every sensible rule is close to perfect."),
  P("The rule itself is short enough to state in one sentence. For each candidate alpha it runs UN-CCD, notes the number of clusters k and the silhouette, and subtracts the silhouette that k-means reaches with the same k on five structureless Gaussian samples having the data's mean and covariance. It then keeps the alpha with the largest excess. In other words, it chooses the alpha at which UN-CCD's clustering looks most clearly better than what the same number of clusters would achieve on data with no clusters at all. The principle of calibrating against a featureless reference is not new; it is the idea behind the gap statistic of Tibshirani, Walther and Hastie (2001). What is new is its use to set UN-CCD's alpha, and its pre-registered test against your own setting. It matters that the plain maximum-silhouette rule, which the agents started from, did no better than your schedule on the test (0.865), so the calibration step is where the gain comes from."),
  P("H2 fails, as the agents themselves predicted before the test was run. Their best formula, alpha = 240 / (n d²), scored 0.045 below the rule (interval 0.021 to 0.074 below). The reason is instructive: most of the rule's advantage comes from treating differently datasets that share the same size and dimension, which no formula in n and d can do. The formula is still worth knowing about. With a single constant it matched your whole schedule (0.020 better, interval from 0.009 worse to 0.051 better) and extends it to any n and d. It amounts to holding the expected number of chance rejections, n times alpha, near 240 / d². The agents also looked for a label-free rule for switching to the descending scan, and found none that helped robustly."),
  P("On the five real test datasets (aggregation, compound, glass, jain and yeast) the picture is much less informative. UN-CCD separates these clusters poorly at any alpha: even the label-using oracle averages only 0.27, and the agents' rule (0.220) and your schedule (0.242) sit close to each other and to that low ceiling. These five datasets therefore say more about the method's reach than about how alpha is chosen."),
);

children.push(
  H1("What we think it means for the paper"),
  P("Taken together, the two projects say that the paper is sound on the kind of data it studies. Its main simulation results come out of its code, on its own datasets, and in one cell the code does better than the paper reports. The one practical weakness, that alpha had to be tuned by hand against the labels, can be removed. A short, label-free rule chooses alpha better than the hand-tuned schedule on new kinds of synthetic data, by a margin larger than the schedule's own advantage over a fixed 1 percent. That makes UN-CCD more practical than the paper itself shows, and it turns the hope that the method needs little tuning into a tested result."),
  P("The real-data comparison would benefit from revision. The values in Table 13 rest on per-dataset levels and scan directions that the text does not report, several results change considerably under the protocol it does report, three datasets depend on row order, and one baseline entry appears to come from the wrong dataset. Together with the method's weak showing on five fresh real datasets, this suggests some caution in how widely the real-data claims are stated. These are questions rather than conclusions, and you may well have explanations we could not see from the repository."),
);

children.push(
  H1("How much weight to give our results"),
  P("We have tried to be careful about the limits of what we found. The general families of the test data were described in the agents' instructions, and the agents simulated similar data while they worked. The test datasets themselves were secret, so the test shows that the rule carries over to new data of a known kind, not to anything at all. All synthetic data were Gaussian or uniform clusters from your generator. Alpha was chosen from a grid of 15 values, and the rule often chose the smallest, so its preferred value may sometimes lie below the grid. Noise points were left out of the ARI, so the scores measure how well clusters are recovered, not how well noise is set aside. The real-data part has only five datasets. Finally, we have not reproduced the RK-CCD and KS-CCD results, whose null tables are far more costly, or the noise study, which cannot be run from the repository."),
);

children.push(
  H1("Questions for you, and what we can offer"),
  P("Several points only you can settle. We would be grateful to know how the per-dataset alphas and the scan direction for seeds were chosen for Table 13, which settings produced the published five-cluster cell in 20 dimensions, whether the Louvain entry for the asymmetric data was indeed taken from the aggregation row, and whether the more liberal form of the test in the code or the Holm procedure in the text is the one you intend."),
  P("In return, everything we built is yours to use. The reproduction harness, the rebuilt null tables, the row-order check, the validated Python port of UN-CCD and the label-free rule for alpha are all public, together with the sealed test data and the now-revealed seed, so that anyone can repeat the test. We would be glad to prepare any of this as a contribution to your repository, to rerun anything under settings you specify, or to extend the alpha rule to RK-CCD and KS-CCD if that would be useful for a revised version or a follow-up paper."),
  P("Thank you for a clear and stimulating paper. I look forward to hearing your thoughts."),
  P("H. P. Alesso"),
);

children.push(
  H1("Where to find everything"),
  P("The reproduction is on the branch unccd-repro and the alpha study on the branch unccd-alpha-lab of github.com/alessoh/artemis. Two full reports go with this note: Artemis Project 1, Reproducing UN-CCDs from the Authors' Own Code, with every simulation cell, real-data result and code difference; and Artemis Project 2, Choosing UN-CCD's Alpha Without Labels, with the agents' run, the sealed test, the fingerprints of every frozen file and the steps to repeat it. The work was carried out by Claude (Anthropic) working as a research and coding agent at my direction, and every number was checked a second time by an independent calculation that took no part in producing it."),
);

children.push(
  H1("Sources"),
  source("Shi, R., Ceyhan, E. and Billor, N. Clustering with Uniformity- and Neighbor-Based Random Geometric Graphs, arXiv:2501.06268v3", "https://arxiv.org/abs/2501.06268"),
  source("Authors' code and data, commit 9bc8032", "https://github.com/Rui-Shi/Cluster-Catch-Digraphs-for-Clustering-and-Outlier-Detection"),
  source("Tibshirani, R., Walther, G. and Hastie, T. Estimating the number of clusters in a data set via the gap statistic, JRSS B 63 (2001)", "https://doi.org/10.1111/1467-9868.00293"),
  source("Karpathy, A. autoresearch", "https://github.com/karpathy/autoresearch"),
  source("Artemis Project 1, reproduction code and results, branch unccd-repro", "https://github.com/alessoh/artemis/tree/unccd-repro"),
  source("Artemis Project 2, program, harness and results, branch unccd-alpha-lab", "https://github.com/alessoh/artemis/tree/unccd-alpha-lab"),
);

const doc = new Document({
  creator: "H. P. Alesso", title: "UN-CCD Reproduced, and Its Alpha Chosen Without Labels",
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
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync("../Artemis_UNCCD_Note_to_Authors.docx", buf); console.log("written"); });
