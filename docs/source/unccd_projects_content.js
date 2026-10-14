// Content for "Artemis Programs in Support of UN-CCDs". Appended to guide_helpers.js at build time.
const children = [];

children.push(
  new Paragraph({ spacing: { before: 600, after: 120 }, children: [new TextRun({ text: "ARTEMIS", font: HEAD_FONT, size: 22, bold: true, color: TEAL, characterSpacing: 120 })] }),
  new Paragraph({ spacing: { after: 160 }, children: [new TextRun({ text: "Six Artemis Programs in Support of Uniformity- and Neighbor-Based Cluster Catch Digraphs", font: HEAD_FONT, size: 36, bold: true, color: INK })] }),
  new Paragraph({ spacing: { after: 400 }, children: [new TextRun({ text: "A review of Shi, Ceyhan and Billor, arXiv:2501.06268v3, and proposed laboratory projects", font: BODY_FONT, size: 24, italics: true, color: MUTED })] }),
);

children.push(
  H1("The paper in brief"),
  P("Rui Shi, Elvan Ceyhan and Nedret Billor of Auburn University propose UN-CCDs, a new member of the Cluster Catch Digraph family of clustering methods. A Cluster Catch Digraph places a ball around every data point, lets each ball \"catch\" the points inside it, selects a small set of balls that together cover the data (an approximate minimum dominating set found greedily), joins overlapping balls into an intersection graph, and finally keeps the grouping that maximizes the silhouette index. Everything therefore depends on how large each ball is allowed to grow. The earlier RK-CCD variant grew each ball until a Monte Carlo test based on Ripley's K function declared that the points inside it were no longer spread uniformly. The new variant replaces Ripley's K with a test based on the mean and median nearest-neighbor distance inside the ball, compared against simulated uniform data and corrected for two tests by Holm's method. The appeal is that nearest-neighbor distances behave far better than Ripley's K as dimension rises, so the method should stay sharp in moderate dimensions while remaining almost free of tuning."),
  P("The evidence comes in two parts. A large simulation study crosses uniform and Gaussian clusters, dimensions 2, 3, 5, 10 and 20, sample sizes from 50 to 500 and two, three or five clusters, each setting repeated 500 times, with uniform background noise added in a separate study. The headline result is that UN-CCDs hold up where RK-CCDs collapse: for three uniform clusters in 20 dimensions with 200 points, the adjusted Rand index (ARI) is 0.921 for UN-CCDs against 0.597 for RK-CCDs, and at five dimensions with 500 points UN-CCDs run in 4.38 minutes against 78.6 for RK-CCDs and 986 for the KS-CCD variant. The second part applies the methods to seven labeled benchmark datasets (iris, seeds, user knowledge, wholesale customers, asymmetric, R15 and D31) against DBSCAN, minimum spanning tree clustering, spectral clustering, K-means++ and Louvain."),
);

children.push(
  H1("What the paper does well"),
  P("The idea is clean and well motivated. Replacing a statistic that is known to degrade with dimension by one whose null distribution is easy to simulate is exactly the kind of first-principles repair that tends to last, and the simulation results show the repair working where it should, in the 10 and 20 dimensional settings where Ripley's K fails. The authors are also unusually candid about scope. Their conclusion names the cubic cost in sample size, the decline of distance-based structure in high dimension, the restriction to uniform background noise, and the difficulty of overlapping or close low-intensity clusters, and it closes with six concrete directions for future work. Finally, the code is public, written in R, and organized so that an outside researcher can rerun it from a fresh clone. That last point matters a great deal here, because it means every project below can start from the authors' own implementation rather than from a reconstruction."),
);

children.push(
  H1("Where the evidence is thinnest"),
  P("A careful reader will notice several places where the claims run a little ahead of the evidence, and these are the natural targets for a laboratory like Artemis. The first is the choice of the significance level α. The paper describes UN-CCDs as requiring little tuning, yet α is set to 15, 10, 5, 1 and 0.1 percent as dimension rises from 2 to 20, and the text says these values were found \"after some trial-and-error process (not shown here)\" to give \"the optimal performance\". Optimal performance can only be judged with the true labels, so the simulation tables report a method whose one parameter was tuned on the answer key. The same is true of the RK-CCD schedule and of the MST threshold used for comparison. This does not make the results wrong, but it means the published numbers are upper bounds on what a user without labels would obtain."),
  P("The second is the real-data summary. The text states that RK-CCDs and UN-CCDs matched or slightly exceeded K-means++ and spectral clustering even when those methods were given the true number of clusters. Table 13 does not quite support this. UN-CCDs beat K-means++ on iris (ARI 0.599 against 0.590) and on R15 (0.975 against 0.894), but K-means++ is clearly ahead on seeds (0.773 against 0.509), user knowledge (0.202 against 0.091), asymmetric (0.882 against 0.736) and D31 (0.912 against 0.799). A fair summary is that UN-CCDs are competitive without being told the number of clusters, which is a real and useful property, rather than that they match methods that are told it."),
  P("The third is uncertainty. The simulation tables report averages over 500 repetitions without standard errors, and each real dataset is clustered once. Because the greedy steps pick the first of several equally good balls, and because several standard datasets, iris among them, are stored sorted by class, the result on a real dataset may depend on the order of its rows. I have not tested whether it does; the point is that the paper gives no way to tell. The fourth is the comparison set. The paper's own setting, clusters of varying shape against uniform background noise, is the home ground of HDBSCAN, OPTICS and Gaussian mixtures with a noise component, and none of these is included. The noise study also stops at 20 percent uniform noise and at 20 dimensions. None of these gaps is unusual for a methods paper, and each can be closed by computation alone, which is why they suit Artemis."),
);

children.push(
  H1("How Artemis would be adapted"),
  P("Artemis was built around a pattern that carries over to clustering without change in principle. A frozen harness, fingerprinted with SHA-256, holds the data generators with their seeds, the real datasets, the reference implementation and the scoring function. A single mutable file, experiment.py, is the only thing the agents may edit. A human-written program.md states the question, the pre-registered hypotheses, the budget and the rule for keeping an idea, which in the Langlands run was a paired bootstrap that an idea had to pass before it was kept. A final test set is sealed and opened exactly once, and an independent session replicates the final number."),
  P("Two practical adaptations are needed. The authors' code is in R, while Artemis and its harness are in Python, so each program would begin by adding R to the Modal image and running the authors' scripts unchanged through a subprocess as the reference. Where a program needs speed or new variants, the harness would also carry a Python port of UN-CCDs, and that port would be frozen only after it reproduces the R implementation on a fixed panel of datasets to within a stated tolerance. The second adaptation is a lesson carried over from the Langlands run, where an auditing agent discovered that the order of curves in the standard tables leaked their rank. The clustering analogue is row order: every real dataset in the harness would be shuffled with a frozen permutation, and the harness would refuse any experiment whose labels can be recovered from the row index."),
  P("The projects below are ordered by how directly they support the paper. The first three test and strengthen what the paper already claims; the last three pursue the authors' own list of future work."),
);

children.push(
  H1("Project 1. Independent reproduction and uncertainty audit"),
  P("**Aim.** Reproduce the paper's central simulation results and Table 13 from the authors' public code, and attach honest uncertainty to every number. This is the project that makes the others credible, because each later program uses its outputs as the baseline."),
  P("**Design.** This is not an agent search but the replication arm of Artemis, the same role an independent session played in the Langlands run. The harness runs the authors' R scripts for UN-CCDs, RK-CCDs and KS-CCDs with recorded seeds, reports each simulation cell as a mean with a bootstrap confidence interval, and reruns every real dataset under 100 frozen row permutations, reporting the spread of ARI, silhouette and number of clusters. It also checks the ARI claims in the real-data summary against the table, and times each method on the same hardware so that the runtime comparison can be extended to DBSCAN and K-means++, which the paper does not time."),
  P("**What success would mean.** A reproduction report the authors could cite, showing which results are stable and which move with the seed or row order. If the numbers reproduce, the paper gains an independent confirmation; if some do not, the authors learn it before a referee does. Because a full rerun of all 120 simulation cells at 500 repetitions could be expensive, the program would start with a pilot on the cells the paper's conclusions lean on most, namely the 10 and 20 dimensional settings and the noise study, and extrapolate the cost from there. I do not yet know the true cost, because the paper's runtime table may report time per repetition or per setting, and I have not run the code."),
);

children.push(
  H1("Project 2. Choosing α without labels"),
  P("**Aim.** The authors' fourth item of future work is to automate the choice of α. This is the cleanest fit for the AutoResearch pattern, because it is a single decision with a frozen, objective judge."),
  P("**Design.** The agents write, in experiment.py, a rule that maps a dataset to a value of α using only the unlabeled data. The rule may look at the sample size, the dimension, the distribution of nearest-neighbor distances, the stability of the clustering under resampling, the silhouette across a grid of α values, or anything else that does not touch the labels. The harness generates training regimes from the paper's own design and a sealed set of held-out regimes the agents never see, with new cluster centers, dimensions between the paper's grid points such as 4, 7 and 15, sample sizes outside the paper's range and noise levels up to 30 percent. The score is the mean ARI across regimes, and an idea is kept only if it beats the incumbent under a paired bootstrap across regimes."),
  P("**Pre-registered hypotheses.** The first is that a label-free rule can match, within 0.02 in mean ARI, the paper's hand-tuned schedule, which was chosen with the labels. The second is that the best rule depends on dimension mainly through the expected scaling of nearest-neighbor distance with sample size and dimension, so that a two-parameter formula captures most of the gain. The sealed final test would be the held-out regimes together with the real datasets already collected in the authors' repository but not used in Table 13, such as aggregation, compound, jain, glass and yeast."),
  P("**What success would mean.** If the first hypothesis holds, the claim that UN-CCDs need little tuning becomes true without qualification, which is the single most valuable improvement Artemis could offer the paper."),
);

children.push(
  H1("Project 3. A faster UN-CCD with the same answers"),
  P("**Aim.** The authors' fifth item is to reduce the computational burden. The method is cubic in sample size, which limits it to a few thousand points."),
  P("**Design.** Here the frozen harness is a non-inferiority test. The agents may change anything about how UN-CCDs are computed, but the harness requires that ARI on a fixed panel of simulated and real datasets stay within 0.005 of the reference implementation from Project 1, and it measures wall-clock time on a fixed container at sample sizes from 500 to 5,000. The score is the median speedup, and an idea that breaks the accuracy tolerance is rejected outright. The repository already precomputes the Monte Carlo null quantiles in lookup tables, so that obvious saving is taken; the remaining candidates are spatial indexes such as k-d trees and ball trees for the distance scans, computing radii only for points that can still enter the dominating set, sparse representations of the catch and intersection graphs, and incremental updates of the silhouette during the merging step."),
  P("**What success would mean.** A drop-in implementation, ideally in Python and contributed back to the authors, that extends the method to datasets an order of magnitude larger with unchanged results. The speedup itself is the claim, and it is easy for a referee to verify."),
);

children.push(
  H1("Project 4. Mapping where UN-CCDs win and where they fail"),
  P("**Aim.** Replace the paper's statement of scope, which is given in words, with a measured map that includes the strongest modern competitors."),
  P("**Design.** This program turns the Skeptic role in Artemis into the main actor. The harness fixes a family of data-generating processes with a small number of knobs: dimension, sample size, number and shape of clusters, separation, the fraction of noise and its type (uniform, Gaussian clutter, or structured noise along lines and sheets). It also fixes a set of baselines run with standard label-free settings, namely HDBSCAN, OPTICS, DBSCAN, Gaussian mixtures selected by BIC with a uniform noise component, K-means++ with the number of clusters chosen by silhouette, and spectral clustering. The agents' experiment.py proposes regimes inside that family, and the harness scores each regime by the gap between UN-CCDs and the best baseline. The agents are rewarded for finding both the regimes where UN-CCDs win by the widest margin and those where they lose by the widest margin, and every regime they report is rerun on fresh seeds before it counts."),
  P("**What success would mean.** A phase diagram showing, for example, at which noise fraction and separation UN-CCDs overtake HDBSCAN, and where they stop doing so. A paper that can say precisely where a method should and should not be used is more useful, and more likely to be cited, than one that shows only favorable settings. This project carries a real risk for the paper, since the map may show HDBSCAN dominating large regions, and the authors should know that before agreeing to it."),
);

children.push(
  H1("Project 5. Beyond twenty dimensions"),
  P("**Aim.** The authors' sixth item is to improve the method in substantially higher dimensions, perhaps through other distances. The paper stops at 20 dimensions."),
  P("**Design.** The harness extends the paper's simulation design to 50, 100 and 200 dimensions, including the common case in which the clusters live in a low-dimensional subspace and the remaining coordinates are noise, and adds real high-dimensional labeled data from public sources, such as the waveform and phishing data already in the authors' repository and further datasets from the UCI and OpenML collections. The agents may change the distance used in the nearest-neighbor test, for example to fractional norms, cosine distance or shared-nearest-neighbor distance; they may add a projection step such as PCA or random projection before the test; or they may replace raw distances with neighbor ranks, whose null distribution does not depend on dimension. In every case the uniform null must be simulated in the same space as the test, a constraint the harness enforces by generating the null itself."),
  P("**What success would mean.** A variant that keeps its ARI above a stated level as dimension grows, or a clear demonstration that no distance in the candidate set rescues the method beyond a given dimension. Both outcomes are publishable as an extension of the paper."),
);

children.push(
  H1("Project 6. Local radii and overlapping clusters"),
  P("**Aim.** The authors' first and third items are to handle overlapping clusters and to adapt the radius to local density. These are the most open-ended directions and the least certain to succeed."),
  P("**Design.** The harness generates pairs and triples of clusters with controlled overlap and contrasting densities, the setting where, on the paper's asymmetric dataset, every CCD variant failed to separate three close elongated clusters and found four clusters instead of five. The agents may let α vary with local density, replace the hard ball membership with soft membership so that points in an overlap belong partly to two clusters, or change the merging rule in the intersection graph. Because soft assignments need a different score, the harness would judge them with a fuzzy version of the adjusted Rand index fixed in advance, alongside the ordinary ARI after hard assignment."),
  P("**What success would mean.** A modest gain on the overlapping regimes without a loss elsewhere would justify a follow-up paper. I would treat this program as exploratory and run it last, because there is no guarantee that a ball-covering method can be made to handle true overlap gracefully."),
);

children.push(
  H1("The six programs at a glance"),
  table(
    [1500, 2300, 2500, 3060],
    ["Program", "Question from the paper", "Frozen judge", "Sealed final test"],
    [
      ["1. Reproduction", "Do the published results hold, and how uncertain are they?", "Authors' R code, recorded seeds, 100 row permutations", "Not a search; independent rerun of every reported number"],
      ["2. Label-free α", "Future work (4): automate α", "Mean ARI across regimes, paired bootstrap keep rule", "Held-out regimes and unused repository datasets"],
      ["3. Speed", "Future work (5): reduce cost", "Median speedup with ARI within 0.005 of reference", "Fresh datasets up to 5,000 points"],
      ["4. Scope map", "Stated limitations; missing baselines", "Gap to best of HDBSCAN, OPTICS, GMM and others", "Every reported regime rerun on fresh seeds"],
      ["5. High dimension", "Future work (6): beyond d = 20", "ARI at 50 to 200 dimensions, null simulated in the test space", "Held-out real high-dimensional datasets"],
      ["6. Overlap and local radii", "Future work (1) and (3)", "Fuzzy and hard ARI on overlap regimes", "Held-out overlap regimes"],
    ],
  ),
  Spacer(),
);

children.push(
  H1("Recommended order and open questions"),
  P("I would run Project 1 first, because it builds the harness, the R bridge and the Python port that every other program needs, and because its results tell us which of the paper's claims are solid enough to build on. Project 2 should follow, since it answers the authors' own question with the clearest possible test and would strengthen the paper's main selling point. Projects 3 and 4 can then run in parallel, and Projects 5 and 6 are best left until the earlier results show where effort is worth spending."),
  P("Several things I do not yet know should be settled before committing compute. I have read the paper and looked at the layout of the authors' repository, but I have not run their code, so I cannot yet say how long a full reproduction takes or whether the published numbers come out exactly. The repository's revision notes map published numbers to scripts for two companion papers on outlier detection, but I did not find an equivalent map for this clustering paper, so part of Project 1 would be building one. Finally, it would be courteous and practical to contact the authors before publishing anything that bears on their results, both to confirm how the α schedule was chosen and to offer the reproduction and any faster implementation back to their repository."),
  P("The Langlands run used Claude Opus 5.5 for the Planner, Experimenters, Skeptic and Scribe and Claude Haiku 4.5 for the Scout, and the same roster would serve here. If you would prefer a different mix, the closed alternatives include Claude Sonnet 5.5 as a cheaper experimenter and the current OpenAI and Google models, and the open-weight alternatives include the Qwen, DeepSeek, Llama and Mistral families, which could run on Modal for the high-volume experimenter role. Please tell me which models you would like before I write the harness and program.md for the first program."),
);

children.push(
  H1("Sources"),
  source("Shi, R., Ceyhan, E. and Billor, N. Clustering with Uniformity- and Neighbor-Based Random Geometric Graphs, arXiv:2501.06268v3, 14 April 2026", "https://arxiv.org/abs/2501.06268"),
  source("Authors' code and data, Cluster Catch Digraphs for Clustering and Outlier Detection (commit 9bc8032, 9 October 2026)", "https://github.com/Rui-Shi/Cluster-Catch-Digraphs-for-Clustering-and-Outlier-Detection"),
  source("Artemis laboratory, branch langlands-lab", "https://github.com/alessoh/artemis"),
);

const doc = new Document({
  creator: "H. P. Alesso", title: "Six Artemis Programs in Support of UN-CCDs",
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
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync("../Artemis_UNCCD_Projects.docx", buf); console.log("written"); });
