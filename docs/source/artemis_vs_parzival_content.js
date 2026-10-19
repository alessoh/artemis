// Content for "Artemis and Parzival: A Capability Review". Appended to guide_helpers.js at build time.
const children = [];

children.push(
  new Paragraph({ spacing: { before: 600, after: 120 }, children: [new TextRun({ text: "CAPABILITY REVIEW", font: HEAD_FONT, size: 22, bold: true, color: TEAL, characterSpacing: 120 })] }),
  new Paragraph({ spacing: { after: 160 }, children: [new TextRun({ text: "Artemis and Parzival: How Much More Can Artemis Do?", font: HEAD_FONT, size: 38, bold: true, color: INK })] }),
  new Paragraph({ spacing: { after: 400 }, children: [new TextRun({ text: "A comparison based on the code and records in github.com/alessoh/parzival and github.com/alessoh/artemis, 19 October 2026", font: BODY_FONT, size: 24, italics: true, color: MUTED })] }),
);

children.push(
  H1("The short answer"),
  P("Artemis and Parzival descend from the same idea, Karpathy's autoresearch pattern of a frozen harness, one file the agent may change and an instruction file written by a human, but they have grown into different kinds of system. Parzival is a single agent that tunes one benchmark, the validation bits per byte of a small language model trained for five minutes on an H100, while sharing results with a swarm of other agents. Artemis is a general laboratory: a team of agents with distinct roles that can be pointed at any question that can be scored by a frozen program, with the honesty of the result enforced by code rather than by instruction, and with every claim tested once on sealed data and then replicated."),
  P("On the abilities that matter for producing scientific results that other people can trust, Artemis is far ahead, roughly a generation beyond Parzival; on the scorecard below it rates 38 of 50 against Parzival's 18, with the caveat that those numbers are my judgement, not a measurement. Parzival is genuinely stronger in two respects that Artemis lacks: it trains real neural networks on a GPU at about eleven experiments an hour, and it collaborates with more than a hundred other agents through a shared memory. Those are worth borrowing."),
);

children.push(
  H1("What Parzival is"),
  P("The Parzival repository holds one commit, made on 5 August 2026, on the branch autoresearch/aug5. I compared every file with its two parents, the swarm fork mutable-state-inc/autoresearch-at-home and Karpathy's original. Apart from its own README, every file but one is byte-for-byte identical to the swarm fork: the harness prepare.py, the instructions program.md, the swarm protocol collab.md, the 1,318-line coordinator client, the setup script, the notebook, the progress chart and the package lock. The single file that differs is train.py."),
  P("That train.py is, by its own header, the champion training script of another participant, Recursive (Apache-2.0, \"Mean validation BPB: 0.9109 (10 seeds)\" on a B200), with nine settings changed through environment defaults: the model width from 768 to 640, a smaller n-gram table, retuned learning rates and warmdown, and a faster compiler mode. The header reports an eight-seed mean of about 0.9365 on an H100, against about 0.944 for Recursive's recipe on the same card, an improvement of roughly 0.8 percent. Reporting a mean over eight seeds is good practice, and choosing a smaller model for a fixed five-minute budget is a sound idea."),
  P("Several things in the repository do not line up, and they matter for an evaluation. The README describes the repository as \"the git history of every improvement it has kept\" with a results ledger and training logs, but there is only one commit, and results.tsv and the logs are excluded by .gitignore, so none of the experiments can be inspected. The README lists the kept improvements as a faster dataloader, multiprocessing, shard tuning, a warmup change and a learning-rate change, while the header of train.py lists a different set. The README gives a best of about 0.9350 and the header a mean of 0.9365, and the header says the matrix learning rate went to 0.05 while the code sets 0.045. The leaderboard position, sixth of 137, may well be correct, but I could not confirm it: the Ensue lab page (ensue-network.ai/lab/autoresearch) draws its leaderboard with JavaScript, so a plain fetch returns no rankings, the site cannot be reached from my workspace, and a web search found no record of Parzival's standing. A screenshot of the live page would settle it. None of this is improper; it is the record of a quick hackathon entry. But it means Parzival's results rest on its README rather than on evidence anyone can check."),
);

children.push(
  H1("What Artemis is"),
  P("Artemis is original code, about 15,000 lines across five branches: a shared core of about 1,000 lines, a frozen harness and agent team for each research program (1,600 to 2,700 lines each), launch and audit scripts, and a public website with an intake agent for proposing problems. Each program has a lead agent and five specialists, a Scout for the literature, a Planner, parallel Experimenters, a Skeptic with a veto and a Scribe, running in Omnigent inside Modal sandboxes."),
  P("Its distinguishing feature is that integrity is enforced by the software. The harness and data are fingerprinted with SHA-256 and checked before every evaluation; the agents' code is screened by a static allowlist and blocked at run time from files, processes and the network; evaluations are budgeted; a change is kept only if a paired bootstrap shows it beats the incumbent by a margin fixed in advance; hypotheses are committed publicly before the run; and the final test, drawn from data the agents never see and sometimes from a secret seed committed by hash, is run exactly once and then reproduced by a separate session. Parzival, by contrast, asks the agent not to modify the harness, keeps a change if a single noisy run improves on the best, and uses the same validation set for every decision, with no held-out test at all."),
  P("Artemis has also produced a body of checked results in four different fields. In materials science it found all four target solar absorbers in 8 evaluations against 20 for the textbook rule. In operations research its routing method beat a state-of-the-art solver on large problems by 0.66 percentage points, significant on held-out instances. In number theory it found a small but certain link between local signs and rank among elliptic curves of the same conductor, replicated exactly and written up as a 13-page paper now ready for arXiv. And in statistics it reproduced an outside paper from the authors' own code and then found a label-free rule that beat the authors' hand-tuned setting on 90 sealed test datasets. Its pre-run audit also caught a data leak, an ordering of Cremona's tables correlated with rank, that a looser harness such as Parzival's would have rewarded."),
);

children.push(
  H1("Side by side"),
  P("Table 1 rates the two systems on ten abilities, from 0 (absent) to 5 (as good as current practice allows). The ratings are my judgement from the code and records; the notes say what each rests on."),
  table(
    [2350, 900, 900, 5210],
    ["Ability", "Parzival", "Artemis", "Basis"],
    [
      ["Range of problems", "1", "4", "Parzival is tied to one benchmark; Artemis has run five programs in four fields and takes any question a frozen program can score."],
      ["Agent organisation", "2", "4", "One agent per machine against a team of six roles with a Skeptic's veto."],
      ["Integrity enforced by code", "1", "5", "Instruction only, against fingerprints, allowlist, run-time blocking and an audit before each run."],
      ["Statistical rigour", "2", "5", "Single-run keep rule and no held-out test (the eight-seed mean is a plus), against paired bootstrap, pre-registration and one sealed test."],
      ["Records others can check", "1", "4", "No ledger or logs in the repository, against public results, frozen files and replications (Artemis's own ledgers stayed in the sandboxes)."],
      ["Verified results", "1", "5", "One tuned configuration with unconfirmed claims, against held-out results in four fields, the routing, number-theory and clustering results independently reproduced."],
      ["Original contribution in code", "1", "4", "Nine settings on another team's script, against about 15,000 original lines."],
      ["Reporting and interface", "1", "4", "A README, against reports, a paper and a public website with an intake agent."],
      ["Compute for machine learning", "4", "2", "Real GPU training at about eleven runs an hour, against CPU sandboxes with no GPU program yet."],
      ["Collaboration across agents", "4", "1", "A 137-agent swarm with claims, shared insights and a global best, against isolated runs."],
      ["Total of 50", "18", "38", "A rough guide only; the categories are not of equal weight."],
    ],
  ),
  Caption("Table 1. Ratings from 0 to 5, from the repositories as they stand on 19 October 2026."),
);

children.push(
  H1("Where Parzival is ahead"),
  P("Parzival's two real strengths are the ones Artemis lacks. It runs on a GPU, so each experiment trains a 50-million-parameter model from scratch, and it can run about a hundred such experiments overnight; every Artemis program so far has been a CPU computation, and the solar, routing, number-theory and clustering harnesses could not host a training run. And through the Ensue network it shares its claims, results, insights and hypotheses with more than a hundred other agents, so that no two agents repeat the same experiment and every agent starts from the swarm's best; Artemis's agents talk only to each other within one run, and what one run learns does not carry to the next. Parzival also never stops, which suits an open-ended benchmark, whereas Artemis runs end by design, because a scientific claim needs a fixed endpoint and a single test."),
);

children.push(
  H1("What each could take from the other"),
  P("Artemis would gain most from two additions. A GPU program on Modal, with the same frozen-harness discipline, would let it take on machine-learning questions, and running Karpathy's own benchmark under Artemis rules would be a direct and telling comparison: a sealed test set and seed-averaged keep rule would show how much of the swarm's progress survives held-out evaluation. A shared memory across runs, along the lines of Ensue's results, insights and hypotheses, would let each program start from what earlier programs learned. Artemis should also merge its five branches, since main does not yet contain the routing, number-theory or clustering programs, and find a way to bring its agents' ledgers out of the sandbox."),
  P("Parzival would gain most from committing its results ledger and logs, reconciling the README with train.py, keeping a change only when a seed-averaged result beats the incumbent by more than its noise, and reserving a held-out slice of data for a final check. Those four changes would turn a leaderboard entry into a result others could rely on."),
);

children.push(
  H1("Sources"),
  source("Parzival repository, branch autoresearch/aug5, commit 704e765", "https://github.com/alessoh/parzival"),
  source("autoresearch-at-home, the swarm fork Parzival is built on", "https://github.com/mutable-state-inc/autoresearch-at-home"),
  source("Karpathy, autoresearch", "https://github.com/karpathy/autoresearch"),
  source("Ensue autoresearch lab page (leaderboard rendered in the browser)", "https://www.ensue-network.ai/lab/autoresearch"),
  source("Artemis repository (branches main, cvrp-lab, langlands-lab, unccd-repro, unccd-alpha-lab)", "https://github.com/alessoh/artemis"),
);

const doc = new Document({
  creator: "H. P. Alesso", title: "Artemis and Parzival: A Capability Review",
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
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync("../Artemis_vs_Parzival_Capability_Review.docx", buf); console.log("written"); });
