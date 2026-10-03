// Build "Artemis Architecture Discussion Paper No. 1" as a Word document.
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, ImageRun,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle, Header, Footer,
  PageNumber, PageBreak, ExternalHyperlink, TabStopType,
} = require("docx");

const NAVY = "1F3A5F";
const INK = "14213D";
const MUTED = "5B6577";
const TEAL = "0F766E";
const BODY_FONT = "Georgia";
const HEAD_FONT = "Arial";

// ---------- helpers ----------
function runs(text, base = {}) {
  // Supports **bold** and *italic* inline markers.
  const out = [];
  const re = /(\*\*[^*]+\*\*|\*[^*]+\*)/g;
  let last = 0, m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), ...base }));
    const t = m[0];
    if (t.startsWith("**")) out.push(new TextRun({ text: t.slice(2, -2), bold: true, ...base }));
    else out.push(new TextRun({ text: t.slice(1, -1), italics: true, ...base }));
    last = m.index + t.length;
  }
  if (last < text.length) out.push(new TextRun({ text: text.slice(last), ...base }));
  return out;
}
const P = (text, opts = {}) => new Paragraph({ children: runs(text), spacing: { after: 160, line: 312 }, ...opts });
const H1 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(text)] });
const H2 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(text)] });
const Caption = (text) => new Paragraph({
  alignment: AlignmentType.LEFT, spacing: { before: 80, after: 280 },
  children: runs(text, { size: 18, color: MUTED, font: HEAD_FONT }),
});
const Img = (file, w, h) => new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { before: 200, after: 60 },
  children: [new ImageRun({ type: "png", data: fs.readFileSync(file), transformation: { width: w, height: h } })],
});
const Pull = (text) => new Paragraph({
  spacing: { before: 200, after: 240, line: 320 }, indent: { left: 540, right: 540 },
  border: { left: { style: BorderStyle.SINGLE, size: 18, color: TEAL, space: 12 } },
  children: runs(text, { italics: true, color: INK, size: 23 }),
});

const border = { style: BorderStyle.SINGLE, size: 4, color: "C9CFD8" };
const borders = { top: border, bottom: border, left: border, right: border };
function table(colWidths, header, rows) {
  const total = colWidths.reduce((a, b) => a + b, 0);
  const cell = (text, w, isHead) => new TableCell({
    borders, width: { size: w, type: WidthType.DXA },
    shading: isHead ? { fill: "E8EEF6", type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: { top: 90, bottom: 90, left: 110, right: 110 },
    children: [new Paragraph({
      spacing: { after: 0, line: 264 },
      children: runs(text, { size: 17, font: HEAD_FONT, bold: isHead, color: isHead ? NAVY : INK }),
    })],
  });
  return new Table({
    width: { size: total, type: WidthType.DXA }, columnWidths: colWidths,
    rows: [
      new TableRow({ tableHeader: true, children: header.map((h, i) => cell(h, colWidths[i], true)) }),
      ...rows.map((r) => new TableRow({ cantSplit: true, children: r.map((c, i) => cell(c, colWidths[i], false)) })),
    ],
  });
}
const Spacer = () => new Paragraph({ spacing: { after: 120 }, children: [] });

function source(label, url) {
  return new Paragraph({
    spacing: { after: 100, line: 276 }, indent: { left: 360, hanging: 360 },
    children: [
      new TextRun({ text: label + ". ", size: 19 }),
      new ExternalHyperlink({ link: url, children: [new TextRun({ text: url, style: "Hyperlink", size: 19 })] }),
    ],
  });
}

// ---------- content ----------
const children = [];

// Title block
children.push(
  new Paragraph({ spacing: { before: 1600, after: 120 }, children: [new TextRun({ text: "ARTEMIS", font: HEAD_FONT, size: 22, bold: true, color: TEAL, characterSpacing: 120 })] }),
  new Paragraph({ spacing: { after: 200 }, children: [new TextRun({ text: "An Architecture for Agentic Scientific Discovery", font: HEAD_FONT, size: 52, bold: true, color: INK })] }),
  new Paragraph({ spacing: { after: 600 }, children: [new TextRun({ text: "Discussion Paper No. 1: building the lab from first principles and Karpathy's AutoResearch", font: BODY_FONT, size: 28, italics: true, color: MUTED })] }),
  new Paragraph({
    border: { top: { style: BorderStyle.SINGLE, size: 6, color: NAVY, space: 8 } },
    spacing: { after: 80 }, children: [new TextRun({ text: "Prepared for the Artemis team  ·  7th Global AI Hackathon, Challenge 03", font: HEAD_FONT, size: 20, color: INK })],
  }),
  new Paragraph({ spacing: { after: 80 }, children: [new TextRun({ text: "Saturday, October 3, 2026  ·  Draft for discussion, not a build specification", font: HEAD_FONT, size: 20, color: MUTED })] }),
  new Paragraph({ spacing: { before: 1200 }, children: runs("This paper opens our design conversation. It reviews the challenge brief and the two project repositories, reasons from first principles about what a scientific discovery is made of, proposes an architecture for Artemis built on Omnigent and a generalized version of Karpathy's three-file AutoResearch contract, and closes with the decisions that only you can make. Nothing gets built until you are satisfied; at that point I will write the Claude Code gauntlet prompt.", { size: 21, color: MUTED }) }),
  new Paragraph({ children: [new PageBreak()] }),
);

// 1
children.push(
  H1("1. What the materials tell us"),
  P("The challenge brief is the first owner of our requirements, so it deserves to be read closely. Challenge 03 of the 7th Global AI Hackathon, run by Hack-Nation with Databricks and in collaboration with the MIT Club of Northern California and the MIT Club of Germany, asks teams to build an agentic lab for a Nobel-caliber breakthrough within 24 hours. Its single hard rule is that Omnigent must orchestrate the live discovery workflow, and the judges want to see multiple specialist agents exchanging outputs, using tools, and changing their plan after an experimental result. The scoring weights tell us where to spend effort: Omnigent orchestration carries 30 percent, breakthrough potential 25 percent, discovery acceleration and learning 20 percent, scientific rigor 15 percent, and creativity and responsibility 10 percent. The website, however beautiful, is not scored directly. It earns points only insofar as it makes the orchestration, the science, and the acceleration visible and convincing."),
  P("The brief is also unusually specific about method. It wants one complete loop running from question to evidence, hypothesis, experiment, result, and an updated decision. It asks that at least two candidate tests be designed and that one be chosen on expected learning, feasibility, and cost. It requires citations for factual claims, labels on agent-generated hypotheses, preserved uncertainty, documented controls and human approval gates, and a statement of the validation still needed. Every agent must have a specification of the decision it owns, its tools, its inputs, and its output, and a shared research record must allow every decision to be reconstructed. The submission includes the repository, agent specifications and policies, a two minute demo, cited evidence, experiment code and results, the measured improvement, and the next experiment."),
  P("The two repositories tell a contrasting story. The artemis repository is a clean slate, holding only a README that reads \"scientific research agent orchestration\" and a license file. The parzival repository, on its autoresearch/aug5 branch, is something far more valuable: a working autonomous researcher. It is your fork of the autoresearch@home swarm, which in turn forks Karpathy's March 2026 autoresearch. According to its README, parzival debuted at sixth of 137 agents on August 5, 2026, reached a validation score near 0.9350 bits per byte against a swarm record of 0.8999, and ran roughly eleven experiments per hour, each a single mutation to train.py trained for exactly five minutes on an H100. Most of its kept gains came from making the data pipeline faster, because under a fixed wall clock, speed converts directly into learning."),
  Pull("That one sentence from the parzival README is the 10× thesis in miniature: when the budget per trial is fixed, every second removed from the loop becomes additional discovery."),
  P("Parzival also carries collab.md, the swarm protocol in which agents claim experiments before running them, publish every result with its full source, post an insight explaining why it worked or failed, and publish the logical next hypothesis for others to pick up. That protocol is exactly the structured handoff and shared research record the brief asks for, and it has already been tested by 137 agents. Artemis should inherit it rather than invent something new."),
  P("Finally, I verified the current state of Omnigent, because the whole architecture hangs on it. Omnigent is Databricks' open-source meta-harness for AI agents, released under Apache 2.0 in June 2026 and at version 0.16.0 as of September 29, 2026. It wraps harnesses such as Claude Code, Codex, the Claude Agent SDK, and OpenAI Agents behind a uniform session API. Agents are declared in YAML with an executor, tools that can include MCP servers, Python functions, and sub-agents, and stateful policies that stack at server, agent, and session levels. Sessions run in OS-isolated sandboxes. Most importantly for the website, the server exposes a REST API that includes a Server-Sent Events stream for each session and an endpoint that lists a session's child sessions, which means the live agent tree can be drawn from real data. It can be deployed on Databricks or self-hosted on Modal, Fly, Render, and several other platforms."),
);

// 2
children.push(
  H1("2. First principles: what is a discovery made of?"),
  P("Musk's battery question translates cleanly to science. A computational discovery is assembled from three raw materials. The first is data, and most of the data this challenge points to is free and open, from OpenAlex and arXiv to PubChem, the Materials Project, NIST JARVIS, and OpenML. The second is compute, and a meaningful test often needs only minutes of CPU or GPU time. The third is reasoning, which today is bought by the token at a price that has collapsed. The finished product is a cited, reproducible finding that changes the next scientific decision. Historically that product takes months, yet almost none of those months are spent computing. They are spent reading, waiting, scheduling, deciding, and writing."),
  P("That gap suggests a scientific version of the idiot index: the elapsed time of one discovery cycle divided by the irreducible compute time inside it. In parzival the ratio is close to one, since a cycle of about five and a half minutes contains five minutes of training. For a human researcher moving from a hypothesis to a tested result and an updated decision, the cycle is commonly measured in days or weeks. I do not have a rigorous published figure for that human baseline, and I would rather we measure our own than quote folklore. The principle stands regardless: the high cost of discovery reflects how science is organized, not anything fundamental about the work, and that gap is where Artemis competes. Its job is to drive the idiot index of the discovery cycle toward one for any question that can be expressed as a measurable experiment."),
  P("A second truth comes from asking why AutoResearch works at all. It rests on four properties: a scalar metric the agent cannot tamper with, a fixed budget for every trial, a single mutable surface, and an automatic rule to keep or revert. Remove any one of them and the loop degrades into a chatbot writing essays about experiments it never ran. The central engineering problem for Artemis is therefore not the agents or the website. It is the translation of an open-ended scientific question into those four properties. Humans do that translation slowly and inconsistently, and it is where the most valuable agent in the system will live."),
  P("A third truth is that a result is only worth what people are willing to trust it for. Trust comes from provenance, controls, and an evaluation that nobody could quietly change after seeing the data. That is why the architecture below freezes its evaluation harness and writes every handoff into an append-only record."),
);

// 3
children.push(
  H1("3. Musk's algorithm applied to Artemis"),
  H2("Step one: make the requirements less dumb"),
  P("Every requirement should trace to a named person. Ours have two owners: the hackathon judges, through the brief, and you, through the project instructions. Applying the rule honestly means questioning your requirements as hard as the judges', because requirements from smart people are the ones nobody challenges. Six of them deserve a second look."),
  P("The instruction to write code in Python fits the lab perfectly, since Omnigent, the harness, the scientific tools, and the report builder are all Python. It cannot cover the browser, however, because Three.js runs in JavaScript and a Vercel front end is naturally a TypeScript application. My proposal is Python everywhere except the browser layer, with Vercel Python functions for any server logic that is more than a thin relay. The instruction to deliver realtime updates on Vercel collides with a hard platform limit: Vercel functions stop after 300 seconds on the Hobby plan and 800 seconds on Pro, with a 30 minute ceiling in beta, while a discovery run lasts hours. The lab therefore cannot live on Vercel. Vercel becomes the window and Omnigent becomes the lab."),
  P("The Three.js and AAA requirement is sound, provided the 3D earns its place by showing real structure: the live agent tree drawn from Omnigent's child sessions, a citation network built from real OpenAlex records, or crystal and molecular structures if the flagship problem is in materials or chemistry. Decorative 3D that encodes nothing is a requirement to delete. The comprehensive report should be measured by the brief's evidentiary standard rather than by length, meaning citations, labeled hypotheses, quantified uncertainty, documented controls and approvals, and an explicit list of validation still needed. The blind comparison against the best distillation information sites is a good bar, but I am not certain which sites you mean. If you mean Distill-style explorable explanations, I will need you to name the specific reference pages the critic should compare against."),
  P("The last tension is the most important. You want any client to be able to propose any problem, while the judges want one specific question meaningfully investigated in 24 hours. I propose that Artemis be general in architecture and honest at the door: the intake accepts any problem, but the Compiler agent either turns it into a measurable experiment, narrows it until it can, or explains why it cannot. For the demo we run one flagship investigation end to end."),
  H2("Step two: delete"),
  P("I started from the role diagram in the brief and from the typical AI-scientist pattern, which together suggested about ten agents: a literature reviewer, a hypothesis generator, a data engineer, an experiment designer, an executor, an analyst, a visualizer, a peer reviewer, a safety agent, and a writer. I deleted down to six. The hypothesis generator merged into the Planner, because generating options and choosing among them under a budget is one decision. The data engineer merged into the Compiler, which writes data access once when it builds the frozen harness. The visualizer disappeared entirely, because the website can render the research record directly. The peer reviewer merged into the Skeptic. The safety agent became mostly policy, enforced by Omnigent above the model where no prompt can talk its way past it, with only a thin Sentinel role left to explain and route approvals."),
  P("Deletion went beyond agents. We do not need a custom orchestration framework, because Omnigent is one; we do not need a separate vector database at first, because OpenAlex search and the ledger cover retrieval; and we do not need a paid realtime vendor at first, because Omnigent already streams events. By Musk's rule that one should add back at least ten percent of what was deleted, I expect to restore one element. My bet is a dedicated Data agent if the flagship domain requires heavy cleaning or joining of datasets."),
  H2("Steps three to five: simplify, accelerate, automate"),
  P("Simplification means one ledger schema, one event stream, one metric per investigation, and one mutable file per experiment. Acceleration comes from running several Experimenters in parallel in separate git worktrees, which is the pattern Omnigent's Polly example already uses, from fixed time budgets per trial, from letting the Scout gather evidence while the Compiler drafts the harness, from caching every external API call, and from routing triage work to fast inexpensive models. Automation comes last, as Musk insists: inside its budget the loop never stops, the report writes itself from the ledger, and humans are interrupted only at the gates that matter, which are approving the metric and harness, raising the budget, and authorizing any consequential action."),
);

// 4
children.push(
  H1("4. Generalizing AutoResearch: the three-file contract"),
  P("Karpathy's design survives intact; only the names change, because the files now describe any science rather than one language model. **program.md** remains the human's sole steering lever. It states the objective, the rules, the budget, the simplicity criterion, the list of ideas worth trying, and the NEVER STOP directive bounded by budget and approval gates. Unlike the original, every requirement in it carries the name of the person who set it, which is Musk's first step made literal. **harness.py** replaces prepare.py as the immutable harness. It loads real data from authenticated sources, defines the train and test split, computes the baseline, runs the controls, and contains the sacred evaluate() function that returns one scalar plus diagnostics. **experiment.py** replaces train.py as the single mutable file, where each hypothesis is expressed as code and committed to git before it runs."),
  Img("fig2_loop.png", 600, 353),
  Caption("Figure 1. The three-file contract and the discovery loop it drives. Each stage is owned by one agent, and the Decision stage is shared between the Planner and a human whenever a gate is reached."),
  P("The freeze is what makes results trustworthy. Once the client approves the harness, its SHA-256 hash is written to the ledger and an Omnigent policy denies every write to it for the rest of the investigation. Every evaluate() result is stamped with that hash, so a reader can verify that no result was produced by a quietly modified metric. The harness must include at least one control beyond the baseline, such as a shuffled-label or random-candidate control, so that an improvement means something. Each trial gets a fixed time or compute budget, a crash or timeout counts as a discard, and the keep-or-revert rule is applied exactly as in parzival, including the simplicity criterion that rewards deleting code for equal results."),
  P("The Compiler's process is the heart of Artemis. The client describes a problem in plain language. The Compiler, with the Scout's evidence in hand, proposes up to three measurable formulations, each with a metric, a dataset, a baseline, and an honest note on what the metric does not capture. The client chooses one. The Compiler then drafts harness.py against real data and performs a dry run that computes the baseline and the controls. Only when the client approves that dry run does the harness freeze and the loop begin. If no formulation can be made measurable with available data, Artemis says so plainly rather than producing an impressive report about nothing."),
);

// 5
children.push(
  H1("5. The lab inside Omnigent"),
  P("Each agent below is declared as an Omnigent YAML specification, and together they form one parent session whose children are visible through the API. The table follows the brief's requirement that every agent specify the decision it owns, its tools, and what it passes on."),
  table([1500, 2600, 2700, 2560],
    ["Agent", "Decision it owns", "Tools", "Hands off"],
    [
      ["Compiler", "How the question becomes a measurable experiment, and what is out of scope", "Scout's evidence, dataset APIs, sandboxed Python for the dry run", "program.md, frozen harness.py, baseline and controls"],
      ["Scout", "Which prior evidence is relevant and how strong it is", "OpenAlex, arXiv, Europe PMC, PubChem, Materials Project, NIST JARVIS, OpenML", "Evidence cards with DOI or accession, claim, strength, and source quote under fifteen words"],
      ["Planner", "Which hypotheses to test and which of at least two candidate tests to run under the budget", "Ledger queries, budget state, information-gain scoring", "Experiment specifications with predicted outcome and the reason this test beat the alternatives"],
      ["Experimenter ×N", "How to express a hypothesis in experiment.py, and whether to keep or revert", "Sandboxed worktree, git, harness.py (read only), fixed per-trial budget", "Run results with commit, metric, diagnostics, harness hash, and logs"],
      ["Skeptic", "Whether a result is real, and whether it should reopen an earlier assumption", "Statistics, controls, re-runs with new seeds, a model from a different vendor", "Verdicts that confirm, qualify, or reject, plus any assumption to reopen"],
      ["Scribe", "How the investigation is told, with every claim tied to evidence", "Ledger, evidence cards, run records, Word and PDF builders", "The cited report and the recommended next experiment"],
    ]),
  Spacer(),
  P("The handoffs are typed objects rather than free text: an EvidenceCard, a Hypothesis, an ExperimentSpec, a RunResult, a Verdict, and a Decision, each with a stable identifier and a pointer to its parents. Every object is written to the ledger the moment it is created, which is how the brief's demand that every decision be reconstructible is met by construction. The vocabulary is borrowed from parzival's collab.md, where claims prevent duplicate work, results carry full source, insights explain why, and hypotheses propose the next move. When the Skeptic finds a surprising result, it issues a Verdict that reopens a named assumption, and the Planner must respond to it before spending more budget. That loop back is the moment judges will look for, because it shows the lab changing its mind."),
  P("The Planner chooses between competing tests with an explicit score: expected information gain multiplied by feasibility and divided by cost, where cost is measured in the same budget units the policies enforce. The score and the losing alternatives are recorded, so the report can show not only what the lab did but what it chose not to do and why."),
  P("Safety lives in policy. Stateful Omnigent policies cap spending per session and pause for approval at thresholds, limit tool calls, restrict network egress to an allowlist of scientific APIs, deny any write to the frozen harness, and require human approval before the harness freezes, before the budget rises, and before anything is published outside the lab. For chemistry and biology the Sentinel halts any objective that optimizes for toxicity or pathogenicity and routes the question to a human, and our domain choice should take that into account from the start."),
);

// 6
children.push(
  H1("6. Measuring acceleration honestly"),
  P("The brief says the strength of the evidence matters more than the size of the multiplier, and I agree. For each investigation Artemis names the bottleneck it attacks, then measures two quantities from ledger timestamps: the elapsed time from the question to the first tested hypothesis, and the number of experiments needed to reach a target value of the metric. It compares these against baselines run in the same frozen harness: a single agent working without handoffs, a naive search such as random or grid exploration, and where feasible a timed manual pass by a person. The report states the observed multiplier with its uncertainty, whether that turns out to be 1.5×, 3×, or 10×, and explains what would have to change for the workflow to approach 10× at scale."),
  P("Parzival gives us a head start, because its existing results file and git history are real, timestamped evidence that an autonomous keep-or-revert loop sustains roughly eleven experiments an hour. That is a credible anchor for the throughput side of the argument, whatever flagship domain we choose."),
);

// 7
children.push(
  H1("7. The website"),
  P("A first-principles question comes before the design: Omnigent already ships a web interface, so what does Artemis add? The answer is the scientific layer that a general agent console does not have. Artemis is where a client turns a question into a measurable experiment, watches a metric improve in real time, sees the evidence graph behind every hypothesis, approves the gates that matter, and receives a report fit to hand to a colleague. Everything else should be deleted from the site."),
  Img("fig1_architecture.png", 600, 448),
  Caption("Figure 2. Proposed system architecture. Vercel hosts the experience and a thin server layer; the Omnigent server, on Databricks or a self-hosted platform, runs the lab; an append-only Postgres ledger holds the research record; live scientific sources are reached through MCP and Python tools."),
  P("The browser application is built with Next.js and Three.js on Vercel. Its server layer has three jobs. The Intake API creates an Omnigent session from the client's problem. The Stream Relay proxies the session's Server-Sent Events to the browser and resumes from the last event identifier whenever a function approaches its time limit, so the experience stays live for hours despite Vercel's caps. The Report Builder renders the ledger into the web report and into Word and PDF files. The relay also acts as the trusted proxy that Omnigent's default authentication expects, injecting the user's identity header. That arrangement is only safe if the Omnigent server accepts traffic from Vercel alone, through a shared secret or private networking, and I flag it as the first security item to settle. All credentials live in .env files locally and in Vercel environment variables in production, and none enter the repository."),
  P("Five pages carry the product. **Intake** is a conversation with the Compiler that ends in a chosen formulation, a computed baseline, and an approval. **Mission Control** is the live lab: a Three.js constellation of the actual agent sessions, a metric curve that moves with every kept experiment, and a streaming ledger of keeps, discards, and crashes. **Approvals** is the inbox for human gates. **Evidence Graph** renders the real citation network behind the hypotheses, where every node is a work with a DOI. **Report** presents the finished investigation and exports it. Wherever data does not yet exist, the page shows an honest empty state rather than an invented example, in keeping with your rule against dummy information."),
  P("The visual direction I would propose is a scientific instrument rather than a marketing site: editorial typography, restrained color reserved for meaning, and motion that only ever reflects a real event in the lab. The gauntlet loop will then hold that direction to the AAA bar through a separate, deliberately harsh critic agent that compares screenshots blind against the reference sites you name."),
);

// 8
children.push(
  H1("8. Which models should power the lab?"),
  P("Your instructions ask me to offer open and closed options rather than choose silently. The table pairs each role with a recommendation and alternatives. I deliberately place the Skeptic on a different vendor from the Planner, following the reasoning behind Omnigent's two-headed Debby example: models from different families make less correlated mistakes, which is precisely what a critic needs."),
  table([1500, 2300, 2900, 2660],
    ["Role", "Recommended", "Closed alternatives", "Open-weight alternatives"],
    [
      ["Compiler, Planner, Scribe", "Claude Opus 5.5", "GPT-6 Astra, Claude Sonnet 5.5", "Qwen3.8 Max, MiMo-V2.6-Pro"],
      ["Experimenter", "Claude Sonnet 5.5 in the Claude Code harness", "GPT-5.6 Sol in the Codex harness, Claude Opus 5.5", "GLM-5.3, DeepSeek V4 Pro"],
      ["Skeptic", "GPT-6 Astra", "Gemini 3.5 family", "Qwen3.8 Max"],
      ["Scout triage", "Claude Haiku 4.5", "Gemini 3.5 Flash", "MiMo-V2.6-Flash"],
    ]),
  Spacer(),
  P("Three caveats keep this honest. The open-weight names and the overall ordering come from the BenchLM leaderboard for October 2026, a third-party aggregator whose scores are partly estimated, so they are indicative rather than definitive; GLM-5.1, for example, is documented there as MIT-licensed while newer GLM releases are not fully documented. I confirmed GPT-6 Astra's release through Bloomberg Government reporting, and GPT-5.6 Sol and Gemini 3.5 Flash appear as defaults in Omnigent's own documentation, but I could not confirm the general availability of a Gemini 4 model, so I have left it out. Finally, Claude Fable 5.1 carries additional safeguards around biology, cybersecurity, and language model research and development, so it may be more conservative than we want for a biology problem or an AutoResearch-style training loop; Opus 5.5 is the safer default for those roles. If we run on managed Databricks, model availability will depend on what that workspace's serving endpoints expose, which I cannot see from here."),
);

// 9
children.push(
  H1("9. What I do not know yet"),
  P("Omnigent is labeled alpha, and while I have read its API specification, I have not yet run a session end to end, so the exact shape of its streamed events and their behavior under reconnection still need a short spike before we commit. I do not know whether the managed Databricks sandbox exposes the REST API to an outside website or only to its own interface. I do not know what GPU access you will have during the hackathon beyond the Lightning.ai studio parzival used. I do not know which sites you intend as the AAA reference set. And I do not know how heavily the judges will weigh a custom website against a well-instrumented Omnigent session, although the scoring suggests the orchestration itself must stay front and center in the two minute demo."),
);

// 10
children.push(
  H1("10. Decisions only you can make"),
  P("**The flagship question.** The demo needs one specific scientific question with real data and a metric that can be evaluated in minutes. I see three strong candidates. The first extends parzival into Artemis as an AI research investigation, which offers the strongest existing evidence of acceleration but a weaker claim to breakthrough potential. The second is a materials question, such as screening the Materials Project and NIST JARVIS for stable, earth-abundant solar absorber candidates in a target band gap window, with a surrogate model's ranking validated against held-out computed values; it suits Three.js crystal visualization and carries little dual-use risk. The third is a biomedical question, such as predicting antibacterial activity from PubChem bioassays under a scaffold split, which has high impact but demands more careful safety policy. I lean toward the materials question as the flagship, with parzival's record cited as independent evidence that the loop itself works, but this is your call."),
  P("**Where Omnigent runs.** Managed Databricks pleases the sponsor and simplifies model routing if you have workspace access; self-hosting on Modal gives us GPUs next to the sandboxes and full control of networking. Do you have a Databricks workspace for the event?"),
  P("**Models.** Please confirm or amend the table in section eight, and tell me which provider keys you hold, since every key will live in .env and nowhere else."),
  P("**Languages and plan.** Do you accept Python for the lab and TypeScript for the browser layer, and are you on Vercel's Hobby or Pro plan? The plan changes the relay's reconnection interval and whether the 800 second limit is available."),
  P("**The AAA reference set.** Please name the distillation or information sites the critic should compare against blind, so the bar is concrete rather than a matter of taste."),
  P("**Who may use the intake.** An open intake invites strangers to spend your model budget. I would gate it behind sign-in for the hackathon unless you want a public demo, in which case the spend policies need tighter caps."),
  P("Once these are settled I will revise this paper into a build specification and then write the Claude Code gauntlet prompt, with the fan-out of sub-agents, the per-item loops, and the harsh visual critic you described."),
);

// Sources
children.push(
  H1("Sources"),
  P("Project materials: the Challenge 03 brief (file.pdf in this project); github.com/alessoh/artemis; github.com/alessoh/parzival on branch autoresearch/aug5, including README.md, program.md, and collab.md."),
  source("Omnigent repository, README, agent YAML specification, OpenAPI specification, and changelog for v0.16.0", "https://github.com/omnigent-ai/omnigent"),
  source("IT Brief, Databricks launches open-source Omnigent for AI agents", "https://itbrief.news/story/databricks-launches-open-source-omnigent-for-ai-agents"),
  source("MCP Directory, Omnigent: the meta-harness explained", "https://mcp.directory/blog/omnigent-meta-harness-2026"),
  source("Vercel, Functions limits (updated August 24, 2026)", "https://vercel.com/docs/functions/limitations"),
  source("BenchLM, LLM leaderboard and benchmarks, October 2026", "https://benchlm.ai/md/index.md"),
  source("BenchLM, Best open-source LLM", "https://www.benchlm.ai/blog/posts/best-open-source-llm"),
  source("Bloomberg Government, OpenAI rolls out GPT-6 Astra model with cyber guardrails", "https://news.bgov.com/artificial-intelligence/openai-rolls-out-gpt-6-astra-model-with-cyber-guardrails-1"),
  source("Karpathy, autoresearch (March 2026)", "https://github.com/karpathy/autoresearch"),
);

// ---------- document ----------
const doc = new Document({
  creator: "Claude",
  title: "Artemis: An Architecture for Agentic Scientific Discovery",
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
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "Artemis  ·  Discussion Paper No. 1", font: HEAD_FONT, size: 16, color: MUTED })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: HEAD_FONT, size: 16, color: MUTED })] })] }) },
    children,
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync("Artemis_Architecture_Discussion_Paper_01.docx", buf);
  console.log("written");
});
