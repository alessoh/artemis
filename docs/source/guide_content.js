// Content for "Artemis, Explained Simply". Appended to guide_helpers.js at build time.
const children = [];

children.push(
  new Paragraph({ spacing: { before: 1400, after: 120 }, children: [new TextRun({ text: "ARTEMIS", font: HEAD_FONT, size: 22, bold: true, color: TEAL, characterSpacing: 120 })] }),
  new Paragraph({ spacing: { after: 200 }, children: [new TextRun({ text: "Artemis, Explained Simply", font: HEAD_FONT, size: 52, bold: true, color: INK })] }),
  new Paragraph({ spacing: { after: 600 }, children: [new TextRun({ text: "A plain-language guide to the diagram and the plan", font: BODY_FONT, size: 28, italics: true, color: MUTED })] }),
  new Paragraph({
    border: { top: { style: BorderStyle.SINGLE, size: 6, color: NAVY, space: 8 } },
    spacing: { after: 80 }, children: [new TextRun({ text: "Companion to Discussion Paper No. 1  ·  7th Global AI Hackathon, Challenge 03", font: HEAD_FONT, size: 20, color: INK })],
  }),
  new Paragraph({ spacing: { after: 80 }, children: [new TextRun({ text: "Saturday, October 3, 2026", font: HEAD_FONT, size: 20, color: MUTED })] }),
  new Paragraph({ spacing: { before: 1000 }, children: runs("This guide replaces the crowded diagram in the first paper with a simpler one, explains each piece in everyday language, follows one question through the whole system, and updates the plan for your Vercel Pro and free Databricks accounts.", { size: 21, color: MUTED }) }),
  new Paragraph({ children: [new PageBreak()] }),
);

children.push(
  H1("1. The whole plan in one paragraph"),
  P("Artemis is a website where someone types a science question. Behind the website, a team of six AI agents turns that question into a fair, measurable test, runs that test many times on real public data, keeps only the changes that improve a fixed score, and writes up what it learned with citations. The website lets you watch the work happen live and approve the important decisions. Omnigent, the free software from Databricks that the hackathon requires, is what coordinates the agents and enforces the safety rules. That is all Artemis is. Everything else in this guide is detail about where each part lives and how the parts talk to one another."),
  H2("Why the first diagram was confusing"),
  P("The diagram in Discussion Paper No. 1 tried to show too much at once. It packed four layers and more than twenty boxes into one picture, and it mixed two different ideas: where software runs, and what the agents do. It also contained a mistake of simplification. I drew Omnigent as one box, but Omnigent actually has two separate parts, a server that coordinates and a runner that does the work. I learned this by reading the deployment guide in the Omnigent repository, and the new diagram corrects it. It shows only five pieces and the path that one question takes through them."),
);

children.push(
  H1("2. An analogy: Artemis as a research institute"),
  P("Imagine a small research institute. Visitors arrive at the **reception desk**, where they describe the problem they want studied, and they can watch the work through a **viewing gallery**. Behind the scenes, a **switchboard operator** assigns the work, enforces the building's safety rules, and announces progress over the loudspeaker. The actual science happens at the **lab bench**, where a team of **scientists** with different specialties works together. Every action is written in a **lab notebook** that nobody is allowed to erase, and the scientists draw their facts from a **library** of published research and public data."),
  P("Artemis maps onto that institute exactly. The website is the reception desk and the viewing gallery. The Omnigent Server is the switchboard. The Omnigent Runner is the lab bench. The six agents are the scientists. A Postgres database is the lab notebook. The public science databases are the library."),
  Img("fig_simple.png", 620, 375),
  Caption("Figure 1. The five pieces of Artemis. The numbered circles 1 to 5 name the pieces; the lettered circles a to g follow one question through the system, as described in section 5."),
);

children.push(
  H1("3. The five pieces, one at a time"),
  H2("Piece 1: the Artemis website (on Vercel Pro)"),
  P("This is the only part a visitor ever sees. It has five pages: an intake page where you type the question, a live lab view with the Three.js 3D display, an approvals page, an evidence page showing the research papers behind each idea, and a report page. The website does not do any science itself. Think of it as a window into the lab plus a front door. It runs on your Vercel Pro account, which matters because Pro lets each server function run for up to 800 seconds instead of 300 on the free plan. A lab session lasts much longer than that, so the website simply reconnects to the live feed every few minutes, picking up exactly where it left off, and you never notice the handover."),
  H2("Piece 2: the Omnigent Server (the switchboard)"),
  P("This is the main program from the Omnigent repository you shared, github.com/omnigent-ai/omnigent. It runs all the time as a web service. It opens a lab session when the website asks, keeps the safety rules and spending limits, and broadcasts a live stream of events describing everything that happens. It deliberately holds no AI model keys and runs no agent code, which keeps it small and safe. My recommendation is to run it on Modal, a cloud service that Omnigent ships ready-made instructions for. Section 6 explains why I am not recommending your free Databricks account for this piece, at least not yet."),
  H2("Piece 3: the Omnigent Runner (the lab bench)"),
  P("The runner is the second half of Omnigent, and it is where the work actually happens. It is a separate program that connects to the server over a secure tunnel, holds your AI model keys in a private .env file, runs the six agents, and runs each experiment inside a locked-down sandbox folder so that nothing can damage anything else. I recommend running it in a Modal sandbox, a disposable cloud machine, so that the lab keeps working when your own computer sleeps. For the very first tests it can run on your own desktop instead."),
  H2("Piece 4: the lab notebook (Neon Postgres)"),
  P("Every question, source, hypothesis, experiment, result, decision, and approval is written into a database the moment it happens, and nothing is ever erased. This serves three purposes. The judges require that every decision can be reconstructed. The final report is generated straight from this record, so it cannot claim anything that did not happen. And if anything crashes, the work can resume from the record. I recommend Neon Postgres, which you can add from the Marketplace in your Vercel dashboard."),
  H2("Piece 5: the science libraries"),
  P("These are the real public databases the agents read from, such as OpenAlex and arXiv for research papers, PubChem for chemistry, the Materials Project and NIST JARVIS for materials, Europe PMC for biomedicine, and OpenML for machine learning datasets. Some of them require a free account key, which goes in the .env file and never into the code repository. Artemis never invents example data. If something has not been measured yet, the website says so."),
);

children.push(
  H1("4. The six agents and the three files"),
  P("Each agent is a separate AI with one job. Splitting the work this way is what the hackathon judges score most heavily, because it shows real collaboration and lets each agent check the others."),
  table([1700, 4600, 3060],
    ["Agent", "Its job in plain words", "Like a ..."],
    [
      ["Compiler", "Turns your question into a fair test with one fixed score, using real data, and writes the rules down", "lab director writing the protocol"],
      ["Scout", "Searches the research literature and public databases for what is already known", "research librarian"],
      ["Planner", "Proposes at least two possible experiments and picks the one that teaches the most for the budget", "principal investigator"],
      ["Experimenters", "Try one change at a time, several in parallel, and keep only the changes that improve the score", "bench scientists"],
      ["Skeptic", "Checks each improvement for flukes and tries hard to disprove it", "peer reviewer"],
      ["Scribe", "Writes the final report, tying every claim to a source or an experiment", "science writer"],
    ]),
  Spacer(),
  P("The agents work through three files, borrowed directly from Karpathy's AutoResearch and your own parzival project. **program.md** is the instruction sheet that you write with the Compiler's help: the goal, the rules, the budget, and ideas worth trying. **harness.py** is the referee. It loads the real data and contains the scoring rule, and once you approve it, it is locked so that nobody, human or agent, can move the goalposts afterward. **experiment.py** is the only file the agents are allowed to change. Each attempt edits it, runs it, and gets scored by the referee. A better score means the change is kept, and a worse score means it is undone. This is exactly how parzival reached sixth place on the autoresearch@home leaderboard."),
);

children.push(
  H1("5. Following one question through the system"),
  P("The lettered circles in Figure 1 trace this journey. To make it concrete, imagine the question is \"Which earth-abundant materials could make efficient solar cells?\" This is an illustration of the process only; no results are being claimed."),
  P("**Step a.** You type the question on the intake page of the website."),
  P("**Step b.** The website asks the Omnigent Server to open a new lab session for that question."),
  P("**Step c.** The server wakes the runner, and the runner starts the agents. The Compiler and the Scout propose two or three measurable versions of your question. One might read: rank candidate materials by predicted band gap and stability, and score the ranking against known computed values that are held back from the agents. You pick a version. The Compiler then runs the referee once to compute a starting score, you approve it, and harness.py locks. This is the first human approval gate."),
  P("**Step d.** The agents pull real data from the science libraries, in this example the Materials Project and NIST JARVIS, along with published papers from OpenAlex."),
  P("**Step e.** The Planner chooses which experiments to run. The Experimenters try many short attempts in parallel, each one kept or undone by the referee, and the Skeptic checks every apparent improvement. Every single step is written into the lab notebook as it happens."),
  P("**Step f.** Live progress flows from the runner to the server and from the server to the website. You watch the agents work in the 3D lab view and see the score improve on a chart. If an agent needs permission, for example to spend more of the budget, a request appears on the approvals page and the lab waits for your answer."),
  P("**Step g.** When the budget is used up or progress stalls, the Scribe writes the report from the lab notebook. You read it on the website or download it as a Word or PDF file. It lists what was found, how confident the lab is, which controls were run, and which real-world experiment should come next."),
);

children.push(
  H1("6. What your accounts mean for the plan"),
  H2("Vercel Pro"),
  P("Your Pro account is exactly what the website needs. The 800-second function limit makes the live feed reliable with only occasional invisible reconnections, and the Vercel Marketplace lets us add the Neon database from the same dashboard."),
  H2("Your free Databricks account"),
  P("I checked the Databricks documentation for Free Edition, and four limits matter for us. Outbound internet access is restricted to a limited set of trusted domains, which may block the science databases our agents depend on. Databricks Apps are limited to three per account, and each runs for at most 24 hours after it is started. Free Edition accounts may not be used for commercial purposes. And the Free Edition documentation does not say whether the managed Omnigent service is available. According to Omnigent's own Databricks guide, that managed service is in Beta and is switched on as a preview in a workspace's settings, so it may or may not appear in a free workspace."),
  P("The hackathon brief explicitly accepts either managed Databricks or open-source Omnigent. My recommendation is therefore **Plan A**: run open-source Omnigent ourselves, with the server on Modal and the runner in a Modal sandbox. That gives the agents full internet access to the science databases and gives the website a stable address to connect to. **Plan B** is a bonus rather than a dependency: if your workspace does offer Omnigent, we can also show the lab running there during the demo, which may please the sponsor. You can check quickly by opening your workspace in the browser and adding /omnigent to the end of its address, or by looking for Omnigent under Previews in the workspace settings. If you prefer, I can check it for you in your browser."),
  H2("The Omnigent repository"),
  P("We will not copy or modify the Omnigent repository. We install it as a ready-made package, the same way you would install any Python library, and keep our own work in your artemis repository: the six agent definitions written as Omnigent YAML files, the safety policies, the three-file contract, and the website code. When Omnigent releases updates, we simply upgrade."),
  H2("Accounts and keys you will need"),
  P("You already have Vercel Pro and GitHub. Plan A adds a Modal account. The Neon database comes through your Vercel dashboard. You will also need API keys for whichever AI models we choose, and a free key for any science database that requires one, such as the Materials Project. Every key lives in .env files on your machine and in Vercel's and Modal's secret settings, never in the code. I have not checked current prices for Modal or Neon, so we should review their pricing pages before the event."),
);

children.push(
  H1("7. The build plan in three phases"),
  P("The phases line up with the timeline in the hackathon brief, which allows four hours to choose and verify, fourteen hours to build the discovery loop, and six hours to strengthen the result and prepare the demo."),
  P("**Phase 1: prove the plumbing.** Before building anything clever, we deploy the Omnigent server on Modal, connect a runner, run one simple test agent, and confirm that the website can see its live stream. This takes the biggest unknown off the table early, because if any connection fails we want to learn it in the first hours, not the last."),
  P("**Phase 2: build the lab.** We write the six agent definitions and the safety policies, have the Compiler build the three files for the flagship question, run one complete discovery loop from question to updated decision, and measure how much faster it is than simpler baselines. The measurements come straight from the lab notebook's timestamps."),
  P("**Phase 3: build the website through the gauntlet loop.** Once the lab works, I write the Claude Code prompt you described, in which sub-agents build each page in parallel and a separate, deliberately harsh critic agent compares screenshots against the reference sites you choose, sending work back until it truly looks first class."),
);

children.push(
  H1("8. What I need from you next"),
  P("Five answers will let me turn this into a build specification. First, are you comfortable with Plan A, which means creating a Modal account? Second, which flagship question should the demo investigate? I still lean toward the solar materials question, though the AI research and antibacterial options from the first paper remain open. Third, which AI model keys do you already have? Fourth, which websites should the visual critic compare Artemis against? Fifth, would you like me to check your Databricks workspace for the Omnigent preview?"),
);

children.push(
  H1("Glossary"),
  table([2300, 7060],
    ["Term", "Meaning"],
    [
      ["Vercel", "The hosting service that runs the Artemis website; you have the Pro plan"],
      ["Omnigent", "Free, open-source software from Databricks that coordinates AI agents and enforces safety rules; required by the hackathon"],
      ["Omnigent Server", "The always-on coordinator, or switchboard, that opens sessions and broadcasts live events"],
      ["Omnigent Runner", "The worker, or lab bench, that holds the model keys and actually runs the agents and experiments"],
      ["Modal", "A cloud service that can host both the Omnigent server and the runner's sandbox machines"],
      ["Sandbox", "A locked-down space where an experiment runs without being able to affect anything else"],
      ["Agent", "One AI model given one specific job, its own tools, and its own instructions"],
      ["Policy", "A safety or spending rule that Omnigent enforces outside the AI, so no prompt can talk its way around it"],
      ["Live stream", "A continuous feed of events from Omnigent to the website, technically called Server-Sent Events"],
      ["Lab notebook", "The Neon Postgres database that permanently records every step of an investigation"],
      ["harness.py", "The locked referee file containing the real data and the scoring rule"],
      ["experiment.py", "The only file the agents may change; each attempt is scored by the referee"],
      ["program.md", "Your instruction sheet for the agents: goal, rules, budget, and ideas"],
      [".env", "A private file of secret keys that never goes into the code repository"],
    ]),
  Spacer(),
);

children.push(
  H1("Sources"),
  source("Omnigent repository, deployment guide (deploy/README.md, execution model) and Databricks guide (docs/databricks.md)", "https://github.com/omnigent-ai/omnigent"),
  source("Databricks, Free Edition limitations", "https://docs.databricks.com/aws/en/getting-started/free-edition-limitations"),
  source("Databricks, Free Edition overview", "https://docs.databricks.com/aws/en/getting-started/free-edition"),
  source("Vercel, Functions limits", "https://vercel.com/docs/functions/limitations"),
);

const doc = new Document({
  creator: "Claude",
  title: "Artemis, Explained Simply",
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
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "Artemis  ·  Explained Simply", font: HEAD_FONT, size: 16, color: MUTED })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: HEAD_FONT, size: 16, color: MUTED })] })] }) },
    children,
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync("Artemis_Explained_Simply.docx", buf);
  console.log("written");
});
