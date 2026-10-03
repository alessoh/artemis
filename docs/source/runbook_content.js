// Content for "Artemis Phase 1 Runbook". Appended to guide_helpers.js at build time.
const Code = (lines) => new Paragraph({
  spacing: { before: 80, after: 200, line: 276 },
  shading: { fill: "EEF2F5", type: ShadingType.CLEAR, color: "auto" },
  border: { left: { style: BorderStyle.SINGLE, size: 12, color: TEAL, space: 8 } },
  indent: { left: 200, right: 200 },
  children: lines.flatMap((l, i) => [
    ...(i > 0 ? [new TextRun({ break: 1 })] : []),
    new TextRun({ text: l, font: "Consolas", size: 18, color: INK }),
  ]),
});
const Step = (n, title) => new Paragraph({
  heading: HeadingLevel.HEADING_2,
  children: [new TextRun(`Step ${n}. ${title}`)],
});

const children = [];

children.push(
  new Paragraph({ spacing: { before: 1400, after: 120 }, children: [new TextRun({ text: "ARTEMIS", font: HEAD_FONT, size: 22, bold: true, color: TEAL, characterSpacing: 120 })] }),
  new Paragraph({ spacing: { after: 200 }, children: [new TextRun({ text: "Phase 1 Runbook: Prove the Plumbing", font: HEAD_FONT, size: 52, bold: true, color: INK })] }),
  new Paragraph({ spacing: { after: 600 }, children: [new TextRun({ text: "What is built, what was tested, and the steps you run to bring the lab online", font: BODY_FONT, size: 28, italics: true, color: MUTED })] }),
  new Paragraph({
    border: { top: { style: BorderStyle.SINGLE, size: 6, color: NAVY, space: 8 } },
    spacing: { after: 80 }, children: [new TextRun({ text: "Repository: github.com/alessoh/artemis (commit 590f505)", font: HEAD_FONT, size: 20, color: INK })],
  }),
  new Paragraph({ spacing: { after: 80 }, children: [new TextRun({ text: "Saturday, October 3, 2026", font: HEAD_FONT, size: 20, color: MUTED })] }),
  new Paragraph({ spacing: { before: 1000 }, children: runs("Phase 1 connects every piece of Artemis with one simple test agent. The code is written, tested as far as my workspace allows, and pushed to your artemis repository. Two hops can only be completed from your computer, because my workspace cannot reach Modal and my Vercel connection is not allowed to create projects. This runbook walks you through those steps in about forty minutes.", { size: 21, color: MUTED }) }),
  new Paragraph({ children: [new PageBreak()] }),
);

children.push(
  H1("1. Where Phase 1 stands"),
  P("Everything in the Phase 1 plan now exists as working code in your artemis repository. A Modal deploy file runs the official, unmodified Omnigent 0.16 server and switches on server-managed sandboxes, so every lab session gets its own disposable Modal machine and nothing depends on your laptop staying awake. A tool-free test agent runs on Claude Haiku 4.5. A small Python relay for Vercel creates sessions, sends messages, and streams live events to the browser. The Phase 1 web page shows a five-station signal path that lights up only when a real event from each part of the system arrives. Two scripts complete the set: one generates every secret on your own computer and stores them in Modal, and one smoke test checks each hop and saves a timestamped record of the run."),
  P("I tested all of it against a real Omnigent 0.16.0 server running in my workspace, configured the same way production will be. The tests confirmed that the machine credentials mint a token and that a wrong secret is rejected, that the agent bundle uploads, that sessions are created, that messages reach the agent, that the reply streams through the relay piece by piece rather than in one buffered lump, that history is stored, and that deleting a session cleans it up. The finished page ran in a headless browser in light mode, dark mode, and at phone width with every station turning green and no script errors. I also confirmed that when a sandbox launch fails, the page and the smoke test report the reason clearly instead of hanging."),
  P("Two things remain unproven until you run the steps below, and I want to be plain about them. The first is the Modal sandbox launch with your own Anthropic key: my workspace blocks Modal's servers, so in my tests Omnigent reached the point of calling Modal and stopped with \"Could not connect to the Modal server,\" which confirms the configuration but not the launch. The second is streaming on Vercel's Python runtime, which only a real deployment can confirm. That is exactly why Phase 1 exists: if either fails, we learn it now."),
  H2("What testing caught and fixed"),
  P("Three real problems surfaced during testing, and each is now fixed. The test agent was answering with Claude Opus 5.5 instead of Haiku because I had placed the model setting one level too deep in the agent file; Omnigent reads it from executor.model, and the corrected file now produces Haiku replies. Second, Omnigent holds the first message open until a new sandbox finishes launching, which can take up to two minutes, so my original thirty-second timeout cut it off. The website now creates the session, opens the live stream, and only then sends the message, so you watch the sandbox start rather than staring at a frozen page. Third, network failures used to crash the smoke test; they are now reported as a failed hop with the reason."),
);

children.push(
  H1("2. What you need before starting"),
  P("You need Python 3.11 or newer and git on your computer, plus four things that only you can supply. The first is your Modal account, which you already have. The second is a Modal API token for the Omnigent server, created at modal.com under Settings and then API Tokens; the server uses it to launch the agent sandboxes. The third is a Postgres database: the quickest route is to open pg.new, which creates a free Neon database and shows its connection string, or you can create a Neon database from the Storage tab of your Vercel dashboard. The fourth is your Anthropic API key. None of these values should ever be pasted into a chat, an email, or the repository; the steps below keep them on your computer and in Modal's and Vercel's secret stores."),
);

children.push(
  H1("3. The steps you run"),
  Step(1, "Get the code"),
  P("Open a terminal and run the following. The last line installs the website's libraries and the Modal command-line tool."),
  Code(["git clone https://github.com/alessoh/artemis.git", "cd artemis", "python -m venv .venv", "source .venv/bin/activate        (on Windows: .venv\\Scripts\\activate)", "pip install -r requirements-lab.txt"]),
  Step(2, "Sign in to Modal"),
  P("This opens your browser once and links the Modal tool on your computer to your account."),
  Code(["modal setup"]),
  Step(3, "Create your secrets file"),
  P("This writes a private .env file in the artemis folder. It generates the Omnigent cookie secret, the Omnigent admin login, the machine client secret the website uses, and the website's access code. The file is excluded from git, and re-running the command never overwrites values you have already filled in."),
  Code(["python scripts/make_secrets.py init"]),
  P("Open .env in any text editor and replace the four FILL_ME_IN values: DATABASE_URL with your Neon connection string, MODAL_TOKEN_ID and MODAL_TOKEN_SECRET with the token from your Modal settings, and OMNIGENT_ANTHROPIC_API_KEY with your Anthropic key. Save the file, then check it. The check prints problems by name and never prints a secret value."),
  Code(["python scripts/make_secrets.py check"]),
  Step(4, "Store the secrets in Modal"),
  P("This creates two Modal secrets. The first, artemis-omnigent-deploy, is read by the Omnigent server. The second, artemis-llm, holds only your Anthropic key and is injected into the agent sandboxes, so the server itself never sees it."),
  Code(["python scripts/make_secrets.py modal"]),
  Step(5, "Deploy the Omnigent server"),
  Code(["modal deploy lab/modal_server.py"]),
  P("Modal prints the server's public address when the deploy finishes. I expect it to be https://alessoh--artemis-omnigent-server.modal.run, and that address is already in your .env file. If Modal prints a different one, put the printed address into both OMNIGENT_ACCOUNTS_BASE_URL and OMNIGENT_URL in .env, then run step 4 and step 5 again. The first start takes about a minute while Omnigent sets up its database tables. To confirm it is alive, open the address in your browser: you should see the Omnigent sign-in page, where you can log in with the admin username and password from your .env file."),
  Step(6, "Run the smoke test against the lab"),
  Code(["python scripts/smoke_test.py"]),
  P("This walks every hop in order and prints a pass or fail line for each, with elapsed time. The first sandbox launch may take one to two minutes while Modal pulls the agent image; later launches are faster. A successful run ends with the test agent's three-line reply and the words PHASE 1 PASSED, and it saves a record of the run in the runs folder."),
  Step(7, "Create the Vercel project"),
  P("In your Vercel dashboard at vercel.com/alessohs-projects, choose Add New, then Project, and import the alessoh/artemis repository. Vercel should detect FastAPI on its own. Before pressing Deploy, open Environment Variables and add the four values printed by the command below, marking the two labeled secret as Sensitive. Then deploy."),
  Code(["python scripts/make_secrets.py vercel"]),
  Step(8, "Check the website"),
  P("Open the address Vercel gives you. The first two stations, Website and Omnigent server, should turn green as soon as the page loads. Enter the access code from your .env file and choose Run the check. You should see the sandbox move through its launch stages, then the Claude station turn green as the reply streams in, and finally the message that all stations reported in. To record the same journey from the command line, run the website-mode smoke test with your Vercel address."),
  Code(["python scripts/smoke_test.py --via-website https://YOUR-PROJECT.vercel.app"]),
  Step(9, "Send me the results"),
  P("Paste the output of both smoke tests into our chat. The output contains pass and fail lines, timings, session identifiers, and the agent's reply, but no keys or passwords, so it is safe to share. If a step fails, paste the failing output and the table below will usually point to the cause, and I will take it from there."),
);

children.push(
  H1("4. If something goes wrong"),
  table([2700, 3100, 3560],
    ["What you see", "Most likely cause", "What to do"],
    [
      ["make_secrets.py modal says the Modal CLI is missing or fails to save", "Modal is not installed or not signed in", "Run pip install -r requirements-lab.txt, then modal setup, then repeat step 4"],
      ["modal deploy says a secret was not found", "Step 4 has not run, or ran in another Modal environment", "Run python scripts/make_secrets.py modal, then deploy again"],
      ["The deploy succeeds but the address will not load", "First start is still running database migrations, or the database URL is wrong", "Wait a minute; then read modal app logs artemis-omnigent and check DATABASE_URL"],
      ["Smoke test fails at Server reachable", "OMNIGENT_URL does not match the address Modal printed", "Copy the printed address into both URL lines in .env, repeat steps 4 and 5"],
      ["Smoke test fails at Credentials accepted with 401", "The secrets in Modal and in .env have drifted apart", "Run init, check, and modal again, then redeploy"],
      ["Sandbox stage shows failed", "The Modal token in .env is wrong or your Modal plan blocks sandboxes", "Create a fresh token in Modal settings, update .env, repeat steps 4 and 5"],
      ["The sandbox is ready but the model reports an error", "The Anthropic key in the artemis-llm secret is wrong or has no credit", "Fix OMNIGENT_ANTHROPIC_API_KEY in .env and run step 4 again"],
      ["The website says the relay is not configured", "Vercel environment variables are missing", "Add the four values from step 7 and redeploy the Vercel project"],
      ["The website accepts the code but no events ever appear", "Vercel may be buffering the stream", "Send me the website smoke test output; this is the case Phase 1 is designed to catch"],
    ]),
  Spacer(),
);

children.push(
  H1("5. Costs and how to switch it off"),
  P("According to Omnigent's own Modal guide, the always-on server costs roughly six to eight dollars a month, which fits within the thirty dollars of monthly credit on Modal's Starter plan. Each agent sandbox is billed only while it runs, and the smoke test deletes its session afterwards, which shuts the sandbox down. A single Haiku reply of three lines costs a fraction of a cent. For comparison, one of my local test runs that accidentally used Opus 5.5 cost about two cents, which is the kind of mistake the model fix prevents. To stop the server entirely, run the command below; deploying again later brings it back with all its data, because the database lives in Neon."),
  Code(["modal app stop artemis-omnigent"]),
);

children.push(
  H1("6. After Phase 1 passes"),
  P("Once both smoke tests pass and the website's five stations turn green, the biggest unknown of the project is gone: we will know that a question typed on a Vercel page can reach a team of agents in Modal sandboxes and stream their work back live. Phase 2 then replaces the test agent with the real lab. That means the six specialist agents written as Omnigent agent files, the safety and spending policies, the three-file contract built by the Compiler for the flagship question, and one complete discovery loop measured against simpler baselines. Before starting Phase 2 I will still need your choice of flagship question and your confirmation of the model lineup, and the Phase 1 records in the runs folder become the first entries in the lab's evidence trail."),
);

const doc = new Document({
  creator: "Claude",
  title: "Artemis Phase 1 Runbook",
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
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "Artemis  ·  Phase 1 Runbook", font: HEAD_FONT, size: 16, color: MUTED })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: HEAD_FONT, size: 16, color: MUTED })] })] }) },
    children,
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync("Artemis_Phase1_Runbook.docx", buf);
  console.log("written");
});
