// Content for "Artemis Project 1: Reproducing UN-CCDs". Appended to guide_helpers.js at build time.
const children = [];
// image paragraph kept on the same page as its caption
const ImgK = (file, w, h) => new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { before: 200, after: 60 }, keepNext: true,
  children: [new ImageRun({ type: "png", data: fs.readFileSync(file), transformation: { width: w, height: h } })],
});

children.push(
  new Paragraph({ spacing: { before: 600, after: 120 }, children: [new TextRun({ text: "ARTEMIS  PROJECT 1", font: HEAD_FONT, size: 22, bold: true, color: TEAL, characterSpacing: 120 })] }),
  new Paragraph({ spacing: { after: 160 }, children: [new TextRun({ text: "Reproducing UN-CCDs from the Authors' Own Code", font: HEAD_FONT, size: 38, bold: true, color: INK })] }),
  new Paragraph({ spacing: { after: 400 }, children: [new TextRun({ text: "An independent reproduction of Shi, Ceyhan and Billor, \"Clustering with Uniformity- and Neighbor-Based Random Geometric Graphs\", arXiv:2501.06268v3", font: BODY_FONT, size: 24, italics: true, color: MUTED })] }),
);

children.push(
  H1("Summary"),
  P("We ran the authors' public R code on the paper's simulation settings and on the seven datasets of its Table 13, and compared every number we could regenerate with the published one. The central simulation evidence holds up well. Of the fifteen simulation cells we checked, fourteen reproduce: the published mean adjusted Rand index (ARI) lies inside our 95% confidence interval or within 0.02 of our mean, on the very same simulated datasets the authors used. That includes the paper's headline comparison, three uniform clusters in 20 dimensions with 200 points, where we obtain an ARI of 0.909 (95% interval 0.894 to 0.924) against the published 0.921. The one cell that does not reproduce errs in the paper's disfavour: for five uniform clusters in 20 dimensions the code gives an ARI of 0.916, far better than the published 0.750."),
  P("The real-data results tell a more qualified story. In the original row order and with the authors' own driver settings, five of the seven UN-CCD results in Table 13 reproduce to within 0.01 in ARI with the same number of clusters, most of them to the third decimal. User knowledge comes out 0.012 too high with our first null table and exactly right with an independent second one. D31 does not reproduce: we obtain 0.746 with 30 clusters, or 0.750 with 31 using the second table, against the published 0.799 with 31. But the driver settings that reproduce the table are not the settings the paper describes. The paper says the significance level was 1% for every dataset; the authors' driver uses levels of 5% to 20%, chosen per dataset, and a descending scan for one dataset. Run as the paper describes it, UN-CCD gives materially different results, worse on R15, D31 and seeds and much better on the asymmetric data. Results also depend on the order of the rows: on seeds the ARI ranges from 0.35 to 0.77 across 100 shuffles, on wholesale the number of clusters found ranges from 2 to 54, and on D31 it moves between 29 and 30."),
  P("Most published baseline values also reproduce or lie within the spread of seeded reruns. The clear exception is Louvain clustering on the asymmetric data, where all 100 of our runs give an ARI of 0.561 with 3 clusters against the published 0.805 with 8; the authors' own captured output gives 0.561 with 3 clusters for this dataset and 0.805 with 8 for another dataset, aggregation, so the published entry appears to have been copied from the wrong row. In reading the code beside the paper we also found thirteen places, the Louvain entry among them, where the two differ. None of them overturns the paper's main conclusion, but several should be corrected before publication, and we list them in full."),
);

children.push(
  H1("What we did"),
  P("The work was done as the replication arm of Artemis, the role an independent session played in the Langlands run: no agent edited any code, and the question was only whether the published numbers come out of the published code. The authors' repository was cloned at commit 9bc8032 (9 October 2026) and every file the reproduction reads was fingerprinted with SHA-256, so that any change would stop the harness. The repository carries no licence file, so its code is not copied into ours; our scripts fetch it."),
  P("One ingredient had to be rebuilt. UN-CCD decides how far to grow each covering ball by comparing the mean and median nearest-neighbour distance of the points inside it with their distribution under complete spatial randomness, and these null distributions are stored as Monte Carlo tables that are not in the authors' repository. Their own generator would take days on our two-core machine for the larger datasets, so we wrote an equivalent one that draws one uniform sample per iteration and uses its first k points as the sample of size k, which leaves the distribution of each table entry unchanged. We checked it against the authors' generator in 2 and 10 dimensions, for samples of up to 40 points and 4,000 iterations each, at all six significance levels: the standardised differences between the two generators average between -0.4 and 0.6 with spreads between 0.6 and 1.5, and fewer than 4% exceed 3 in size, which is consistent with agreement up to Monte Carlo error at this test size. Each table uses 10,000 iterations, as the authors' tables do, and for every dimension the real-data driver names we built a second, independent table to see how much results move with Monte Carlo noise."),
  P("The data were rebuilt by evaluating the authors' own loader and simulation drivers, with only the steps that cannot run on another machine removed. For the simulations this matters: the drivers draw all their datasets from one random-number stream seeded with 2024, so by replaying that stream we clustered exactly the datasets the authors clustered, repetition by repetition. For the real data we ran each dataset in its original row order and under 100 random row shuffles (5 for D31, where one run took up to 22 minutes here), and we ran three readings of the protocol: the authors' driver settings, the protocol as the paper states it, and the driver with the null table matched to the data's true dimension where the two differ. The baselines were run through our own short driver with the settings read from the authors' scripts; the authors' K-means++ package could not be installed here, so K-means++ uses an equivalent implementation (k-means++ seeding followed by Lloyd iterations). They were run once for DBSCAN, which is deterministic, and with 100 random seeds for K-means++, spectral clustering and Louvain (fewer for the slowest cases). All criteria for calling a result reproduced were written down before the results were seen and are in the program file on the branch."),
);

children.push(
  H1("The simulations"),
  P("Table 1 sets our results beside the published ones. The two-dimensional cells, run for all 500 repetitions, agree almost exactly for both uniform and Gaussian clusters, which shows that the rebuilt null tables and the replayed data behave as the authors' did. The moderate-dimensional cells are the ones the paper's argument rests on, and they also reproduce in ARI: three uniform clusters in 10 dimensions are recovered perfectly, and in 20 dimensions the two- and three-cluster cells agree with the published ARI to within 0.012. For the three-cluster cell the success rate, the share of repetitions that find exactly three clusters, comes out at 0.762 against the published 0.802, just outside our interval. An independent null table gives 0.752, so Monte Carlo noise in the table does not explain the gap."),
  P("The five-cluster uniform cell in 20 dimensions is the exception, and it fails in an unusual direction. The code recovers the clusters far better than the paper reports, with an ARI of 0.916 against 0.750 and a success rate of 0.674 against 0.284. The authors' own captured log for this cell shows the published numbers, so they did come from a run of their code, but not, it seems, of the code and settings now in the repository. As a post hoc check, which was not among our pre-registered criteria, we reran the first 100 repetitions with two other settings. The ascending scan at 0.1% gives an ARI of 0.895 and a success rate of 0.63, so the scan direction does not explain the gap. A 1% significance level with the descending scan gives an ARI of 0.719 (interval 0.675 to 0.763), which contains the published 0.750, but a success rate of 0.18, below the published 0.284. A run at a level near 1% is therefore a plausible explanation for the ARI, but we cannot confirm it. Either way the published value understates the method."),
  table(
    [2350, 1700, 2600, 900, 1810],
    ["Cell (distribution, d, n, clusters)", "Published ARI / SR", "Reproduced ARI [95% CI] / SR", "Reps", "Verdict"],
    [
      ["Uniform, 2, 50, 2", "0.980 / 0.996", "0.980 [0.972, 0.987] / 0.994", "500", "Reproduced"],
      ["Uniform, 2, 50, 3", "0.926 / 0.902", "0.924 [0.910, 0.937] / 0.900", "500", "Reproduced"],
      ["Uniform, 2, 50, 5", "0.610 / 0.214", "0.614 [0.596, 0.632] / 0.224", "500", "Reproduced"],
      ["Gaussian, 2, 50, 2", "0.930 / 0.988", "0.931 [0.918, 0.944] / 0.986", "500", "Reproduced"],
      ["Gaussian, 2, 50, 3", "0.868 / 0.854", "0.865 [0.848, 0.882] / 0.850", "500", "Reproduced"],
      ["Gaussian, 2, 50, 5", "0.644 / 0.346", "0.650 [0.629, 0.670] / 0.358", "500", "Reproduced"],
      ["Uniform, 5, 500, 2 / 3 / 5", "1.000, 1.000, 0.999", "1.000, 1.000, 0.996 (all SR 1.000)", "20 each", "Reproduced (pilot)"],
      ["Uniform, 10, 200, 3", "0.998 / 0.996", "1.000 [1.000, 1.000] / 1.000", "200", "Reproduced"],
      ["Gaussian, 10, 200, 3", "0.955 / 0.972", "0.948 [0.934, 0.960] / 0.960", "200", "Reproduced"],
      ["Uniform, 20, 200, 2", "0.962 / 0.848", "0.960 [0.952, 0.968] / 0.840", "500", "Reproduced"],
      ["Uniform, 20, 200, 3", "0.921 / 0.802", "0.909 [0.894, 0.924] / 0.762", "500", "Reproduced (ARI); SR lower"],
      ["Uniform, 20, 200, 5", "0.750 / 0.284", "0.916 [0.902, 0.930] / 0.674", "500", "Not reproduced (code does better)"],
      ["Gaussian, 20, 200, 5", "0.439 / 0.134", "0.457 [0.424, 0.492] / 0.195", "200", "Reproduced (ARI); SR higher"],
    ],
  ),
  Caption("Table 1. UN-CCD simulation cells. SR is the success rate, the share of repetitions that find the true number of clusters. Repetitions are the authors' own datasets, replayed from their random-number stream; where fewer than 500 were run they are the first ones. The interval is a bootstrap 95% interval for the mean ARI. The d = 5 row covers three cells."),
);

children.push(
  H1("The real data"),
  P("Figure 1 and Table 2 show UN-CCD on the seven datasets of Table 13. With the authors' driver settings and the rows in their original order, iris, seeds, wholesale and R15 reproduce to the third decimal, and asymmetric to within 0.003. User knowledge gives 0.103 with our first null table and exactly the published 0.091 with the second, which suggests its published value sits inside the Monte Carlo noise of the table, which is worth knowing because it is one of the datasets where UN-CCD is said to beat its CCD rivals. D31 does not reproduce with either table; it is the largest dataset, with 31 small clusters, and its result evidently depends on details we could not recover."),
  ImgK("../results/unccd_repro1/fig_real_data.png", 600, 325),
  Caption("Figure 1. Published UN-CCD ARI (diamonds) against our reproduction in the original row order (dots), with the range over row shuffles (bars). Bars are absent where every shuffle gives the same result."),
  P("Row order matters for three datasets under our pre-registered rule, strongly for two of them. A clustering method should not depend on the order in which the data happen to be stored. On seeds the published 0.509 is what the stored order gives, but across 100 shuffles the ARI runs from 0.35 to 0.77 and the method finds 2 clusters in 42 shuffles, 3 in 23 and 4 in 35 (Figure 2). On wholesale the ARI stays near zero whatever the order, as it does for every method in the paper, but the number of clusters found ranges from 2 to 54, and the published observation that UN-CCD is the only method to identify the correct number of clusters holds in just 11 of the 100 shuffles. On D31 the number of clusters changes from 30 to 29 in two of the five shuffles. The other datasets give the same answer in every shuffle. The covering-ball radii themselves do not depend on the order: a check on seeds found them identical, point for point, under three shuffles, while the clustering still changed. The order dependence therefore enters later, most likely where the greedy steps break ties by taking the first of several equally good candidates."),
  ImgK("../results/unccd_repro1/fig_seeds_order.png", 600, 217),
  Caption("Figure 2. ARI on the seeds data over 100 row shuffles. With the driver's settings (blue; marker shape gives the number of clusters found) the result depends strongly on row order; with the stated protocol (orange) every shuffle gives 0.435."),
  P("The driver settings themselves are the largest issue. Section 5 of the paper says the significance level was set to 1% for every dataset, but the driver uses 10% for iris, 5% for seeds, user knowledge and wholesale, 20% for asymmetric and 15% for R15 and D31, and it switches seeds to the descending scan. These look like per-dataset choices, and since the paper's other parameters were tuned by trial and error against the true labels, a reader would want to know how these were made. Run as the paper describes, with 1% everywhere, the ascending scan of Algorithm 4 and null tables for each dataset's true dimension, UN-CCD gives 0.616 on iris, 0.435 on seeds, 0.083 on user knowledge, a slightly negative value on wholesale, 0.795 with 13 clusters on R15 and about 0.52 with 15 clusters on D31. On the asymmetric data it does much better than published, 0.924, and it finds all five clusters, which the paper reports no CCD variant could do. Keeping the driver's settings but matching the null table to the data's true dimension, which differs from the one the driver names for user knowledge and wholesale, gives 0.147 on user knowledge (0.147 to 0.221 across shuffles) and -0.006 with 2 clusters on wholesale, where no shuffle finds 3."),
  table(
    [1350, 1250, 1500, 1350, 2510, 1450],
    ["Dataset", "Published ARI, k", "Driver, original order", "Second null table", "Shuffles: ARI range; share giving published k", "Stated protocol (1%, ascending)"],
    [
      ["iris", "0.599, 3", "0.599, 3", "0.599, 3", "0.599 in all 100; 100%", "0.616, 3"],
      ["seeds", "0.509, 2", "0.509, 2", "0.509, 2", "0.345 to 0.774; 42%", "0.435, 2"],
      ["user knowledge", "0.091, 2", "0.103, 2", "0.091, 2", "0.103 in all 100; 100%", "0.083, 2"],
      ["wholesale", "0.002, 3", "0.002, 3", "0.002, 3", "-0.004 to 0.029; 11% (k from 2 to 54)", "-0.003, 2"],
      ["asymmetric", "0.736, 4", "0.739, 4", "0.739, 4", "0.739 in all 100; 100%", "0.924, 5"],
      ["R15", "0.975, 15", "0.975, 15", "0.975, 15", "0.975 in all 100; 100%", "0.795, 13"],
      ["D31", "0.799, 31", "0.746, 30", "0.750, 31", "0.740 to 0.747; 0% (k 29 or 30)", "0.524, 15"],
    ],
  ),
  Caption("Table 2. UN-CCD on the Table 13 datasets. k is the number of clusters found. Shuffles are 100 random row orders (5 for D31). The stated protocol uses null tables for each dataset's true dimension. Iris has 147 rows after the loader removes duplicate rows."),
);

children.push(
  H1("The baselines"),
  P("The comparison methods mostly reproduce. DBSCAN, which is deterministic, matches the published values exactly on six datasets and differs by 0.003 on the seventh. For K-means++, spectral clustering and Louvain, which depend on a random start, every published value but two lies within the range of our seeded runs, and several are reproduced exactly by most seeds. Some published values are favourable draws: the K-means++ result on D31, 0.912, is beaten by only 5% of our runs, whose mean is 0.851, and the spectral result on the asymmetric data, 0.975, is the best value any of our 50 runs reached, and only 5 of them reached it. Since the paper uses these single draws to rank the methods, the ranking between UN-CCD and K-means++ on D31 and between UN-CCD and spectral clustering on the asymmetric data is less firm than the table suggests."),
  P("On D31 the slowest baselines could be run only a few times. Louvain's five runs (0.337 to 0.376, with 9 communities) bracket the published 0.371, and spectral clustering's three runs (0.782 to 0.856) all lie above the published 0.778, too few runs to call it a discrepancy. Louvain on the asymmetric data does not reproduce at all: all 100 of our runs give an ARI of 0.561 with 3 communities, against the published 0.805 with 8. The authors' own captured output from their Louvain script explains it: it shows 0.561 with 3 communities for the asymmetric data, as we find, and 0.805 with 8 communities, silhouette 0.479, for the aggregation dataset, which matches the published asymmetric entry in all three numbers. The published value appears to have been copied from the aggregation row, a dataset that does not appear in the paper."),
);

children.push(
  H1("Where the code and the paper differ"),
  P("Reading the code beside the paper turned up the differences in Table 3. We list them without judging how they arose; several are the ordinary residue of a long project, but readers of the paper cannot see them, and some change the results."),
  table(
    [2100, 3150, 4110],
    ["Topic", "Paper", "Code (file and line in the authors' repository)"],
    [
      ["Real-data significance level", "Section 5: alpha is 1% for all datasets.", "Real_Data_UNCCD.R, lines 12 to 205: 5% to 20%, set per dataset."],
      ["Scan direction", "Algorithm 4 scans radii in ascending order; a descending option is mentioned in Section 3.2.", "Descending for seeds (Real_Data_UNCCD.R line 37) and for every simulation with d of 10 or 20."],
      ["Holm correction", "Algorithm 3 rejects randomness if p(1) is at most alpha/2 or p(2) is at most alpha, by Holm's step-down procedure, under which the first condition must hold.", "UN_CCD.R line 268 rejects when either statistic falls below its alpha quantile, that is when p(1) is at most alpha, a more liberal test."],
      ["Simulation entry point", "Algorithm 4 (UN-CCD clustering).", "All 40 simulation drivers call UNMCCD_outlier (e.g. line 54), which the file they load does not define, so they cannot run as committed. The published values are reproduced by UNCCD_clustering, Algorithm 4."],
      ["Null table dimension", "User knowledge d = 6, wholesale d = 8.", "The loader keeps 5 and 6 columns (Real_Data_Collection.R lines 203 and 62), while the driver loads tables named for d = 6 and d = 8."],
      ["Gaussian cluster centres", "Section 4.2: the same centres as the uniform settings.", "cls_dis = 6 in the Gaussian drivers (line 22), so centres sit at 9 rather than 6 along each axis."],
      ["Gaussian covariance", "Delta times the identity, Delta uniform on [0.8, 1.2].", "Uni-Gau_cls.R line 72 scales by radius squared with radius uniform on (0.8, 1.2), so Delta lies in [0.64, 1.44]."],
      ["Gaussian, d = 10", "alpha 1% for d = 10.", "Level 99.9 (alpha 0.1%) in the Gaussian d = 10 drivers; the captured logs hold two runs of these cells and the paper reports the first."],
      ["Spectral baseline", "Gaussian similarity function.", "The distance matrix is passed to kernlab's specc as a data matrix; the Gaussian line is commented out (lines 19 to 23)."],
      ["Normalisation", "Synthetic datasets are not normalised; iris has 150 rows.", "The loader standardises the asymmetric data (line 137); iris has 147 rows after duplicates are removed."],
      ["Noise study", "Section 4.3, 1,000 repetitions per setting.", "No driver for this study is in the repository."],
      ["Table 9", "Caption: RK-CCDs.", "The header row of the same table reads KS-CCDs."],
      ["Table 13, Louvain", "Asymmetric: ARI 0.805, silhouette 0.479, 8 clusters.", "The authors' captured output (Real_Data_Louvain.html) gives these numbers for the aggregation dataset; for asymmetric it gives 0.561, 0.491 and 3."],
    ],
  ),
  Caption("Table 3. Differences between the paper's text and the code in the authors' repository at commit 9bc8032."),
);

children.push(
  H1("What this means for the paper"),
  P("The main claim survives. UN-CCD does hold up in 10 and 20 dimensions where its Ripley's K predecessor fails, and the published simulation numbers come out of the authors' code on the authors' datasets, with one cell where the code does better than the paper says. That is a good result for a methods paper and a credit to the authors' decision to publish their code and to replay their random-number stream exactly."),
  P("The real-data comparison needs revision. The values in Table 13 come from per-dataset significance levels and scan directions that the paper does not report, and under the protocol the paper does report several of them change by large amounts in both directions. Three datasets depend on row order, two of them strongly; some baseline values are favourable single draws; and one baseline entry appears to have been copied from the wrong dataset. A revised table would report the settings actually used, or rerun every dataset at 1%; give each method's result as a mean and range over several row orders and seeds; and say how the per-dataset settings were chosen. The differences in Table 3 should be corrected in the text or the code, and the noise-study scripts added to the repository."),
);

children.push(
  H1("What remains and how to run it"),
  P("Three parts of the full reproduction were beyond a two-core machine. The remaining UN-CCD simulation cells, and the piloted ones at their full 500 repetitions, can be run on Modal with the script lab/unccd/modal_sweep.py under your own Modal account: modal setup once, then modal run lab/unccd/modal_sweep.py --dry-run to count the work, then a single small cell such as --cells \"Uniform/3d/n50/2\" --reps 1:50 to test the setup, then the full run. The script needs no keys or secrets, writes its results into the same folder the local harness reads, and has not yet been tested on Modal, because this workspace has no Modal credentials. It covers all 120 cells, so it also reruns the cells reproduced here as a check. We have not reproduced the RK-CCD and KS-CCD results at all: their null tables and parameter grid cost far more than UN-CCD's, and they are the natural next addition to the sweep. The noise study cannot be reproduced from the repository and would have to be rebuilt from the paper's description."),
  P("Finally, before any of this is published it would be right to send the findings to the authors. Several of the differences may have simple explanations that only they can give, and the reproduction harness, the rebuilt null tables and the order-sensitivity check would all be useful contributions to their repository."),
);

children.push(
  H1("Reproducibility record"),
  P("Everything is on the branch unccd-repro of github.com/alessoh/artemis. The folder lab/unccd holds program.md (the protocol and criteria, with the changes made during the run), prepare_data.py (clones the authors' repository at commit 9bc803219933 and fingerprints the 18 files it reads), null_tables.py (builds and validates the null tables; seeds 20261014 plus d, and 20261514 plus d for the second tables), r/unccd_job.R (runs one job with the authors' functions), harness.py (runs and summarises the jobs) modal_sweep.py and two small checks in the folder checks. The folder docs/results/unccd_repro1 holds summary.json with every number in this report, all_job_results.jsonl.gz with every individual run, the null-table validation files, the outputs of the two checks and the figures. To rerun the real-data part, run python lab/unccd/prepare_data.py, build the tables with null_tables.py, then python lab/unccd/harness.py real and python lab/unccd/harness.py summarize; the real-data jobs took about six hours of computing time and the whole reproduction about fourteen, most of it on D31 and the 20-dimensional simulations."),
  P("The reproduction was carried out by Claude (Anthropic) working as a coding agent at the author's direction, using the authors' code and data. A separate Claude session, which took no part in the work, then checked every number and code reference in this report against the raw results, the paper and the authors' repository; its corrections are included, and its row-order check is the one in the folder checks."),
);

children.push(
  H1("Sources"),
  source("Shi, R., Ceyhan, E. and Billor, N. Clustering with Uniformity- and Neighbor-Based Random Geometric Graphs, arXiv:2501.06268v3, 14 April 2026", "https://arxiv.org/abs/2501.06268"),
  source("Authors' code and data, commit 9bc8032, 9 October 2026", "https://github.com/Rui-Shi/Cluster-Catch-Digraphs-for-Clustering-and-Outlier-Detection"),
  source("Reproduction code and results, branch unccd-repro", "https://github.com/alessoh/artemis/tree/unccd-repro"),
);

const doc = new Document({
  creator: "H. P. Alesso", title: "Artemis Project 1: Reproducing UN-CCDs",
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
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync("../Artemis_UNCCD_Reproduction_Report.docx", buf); console.log("written"); });
