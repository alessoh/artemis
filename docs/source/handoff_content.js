// Content for "Artemis Handoff Report, 19 October 2026". Appended to guide_helpers.js at build time.
const children = [];
const Code = (text) => new Paragraph({
  spacing: { before: 60, after: 60 }, indent: { left: 360, right: 360 },
  children: [new TextRun({ text, font: "Consolas", size: 19, color: INK })],
});

children.push(
  new Paragraph({ spacing: { before: 600, after: 120 }, children: [new TextRun({ text: "ARTEMIS  HANDOFF", font: HEAD_FONT, size: 22, bold: true, color: TEAL, characterSpacing: 120 })] }),
  new Paragraph({ spacing: { after: 160 }, children: [new TextRun({ text: "Where Artemis Stands and How to Pick It Up in a New Chat", font: HEAD_FONT, size: 38, bold: true, color: INK })] }),
  new Paragraph({ spacing: { after: 400 }, children: [new TextRun({ text: "A summary of the work from 3 to 19 October 2026, written as the starting point for the next conversation", font: BODY_FONT, size: 24, italics: true, color: MUTED })] }),
);

children.push(
  H1("Why start a new chat"),
  P("This conversation has run for more than two weeks and has already been compressed once to fit Claude's working memory. Each compression keeps the main facts but loses detail, and a long conversation also slows every reply. Nothing is at risk, because all the work lives on GitHub and in the project's documents, so a fresh chat that reads this report and the status note can carry on without loss. Before writing this report I also moved the one set of files that existed only in Claude's temporary workspace, the arXiv package for the Euler paper, into the repository."),
  P("To begin, open a new chat in the project Artemis, Scientific Discovery, and start with a message such as the following. The same summary is saved in the project as claude/artemis_handoff_2026-10-19.md, which the new chat can read directly."),
  Code("Read claude/artemis_handoff_2026-10-19.md and claude/artemis_phase1_status.md in the project, then clone github.com/alessoh/artemis with all branches. We are continuing from that handoff. Today I want to ..."),
);

children.push(
  H1("The system as it stands"),
  P("Artemis is a public repository, github.com/alessoh/artemis, under an MIT licence. Its agents run in Omnigent 0.16 on Modal, through the server at alessoh--artemis-omnigent-server.modal.run, in managed sandboxes that the website reaches by logging in as artemis-web. The public website is live at artemis-ten-blond.vercel.app, with Results, Method and About pages and a Start an investigation page backed by an intake agent and Neon Postgres. Labs are launched from your Windows computer in Anaconda PowerShell, in the conda environment artemis, with the scripts in the scripts folder."),
  P("The work is spread over five branches, shown in Table 1. The main branch does not yet contain the routing, number theory or clustering programs, so merging the branches is one of the open tasks."),
  table(
    [2000, 1200, 6160],
    ["Branch", "Head", "What it holds"],
    [
      ["main", "119c69f", "The core, the solar lab, the website, the Phase 1 to 3 documents and the hundred research proposals"],
      ["cvrp-lab", "b6a920e", "The vehicle routing program and its two runs"],
      ["langlands-lab", "fb4acb4", "The Langlands and elliptic curve program, its results and replication, and the paper with its arXiv package in docs/paper_euler"],
      ["unccd-repro", "27b191b", "UN-CCD Project 1, the reproduction of Shi, Ceyhan and Billor"],
      ["unccd-alpha-lab", "latest", "UN-CCD Project 2, the note to the authors, the Parzival review and this handoff"],
    ],
  ),
  Caption("Table 1. Branches of github.com/alessoh/artemis on 19 October 2026."),
);

children.push(
  H1("What has been achieved"),
  P("The first three phases built and proved the system: the plumbing worked end to end, and the website went live after 249 automated checks. The solar program, the flagship, searched NIST's JARVIS database for earth-abundant solar absorbers and found all four target materials in 8 evaluations, against 20 for the textbook rule and about 344 for random search. The routing program found that splitting large delivery problems into sectors beats the state-of-the-art PyVRP solver on problems with 500 or more customers, with a gap to the best known solutions of 1.35 percent against 2.01 percent (paired difference 0.66 percentage points, interval 0.50 to 0.81) and a win on 8 of 8 instances, though not on small problems."),
  P("The Langlands program tested your memo on Euler's identity. Over the field Q(√5) the predicted reversal of the murmuration pattern appeared (correlation 0.53), and among elliptic curves of the same conductor the local signs carry a small but certain trace of rank, with held-out scores of 0.522 for the rule fixed in advance and 0.543 for the lab's rule. A separate session reproduced every number. The paper, \"Euler's Identity, Elliptic Curves and an AI Laboratory\", runs to 13 pages and its arXiv package is complete and compiles cleanly."),
  P("The two UN-CCD projects took an outside paper as a test case. Project 1 reproduced 14 of 15 of its simulation results from the authors' own code, and found that the real-data settings differ from those the paper states, that some results depend on row order, and thirteen smaller differences between the code and the text. Project 2 answered the authors' own future-work question: a label-free rule found by the agents chose the method's alpha better than the authors' hand tuning on 90 sealed test datasets, 0.928 against 0.863, close to the label-using ceiling of 0.954. A short, friendly note to the authors with links to both reports is ready. Finally, a review compared Artemis with your earlier Parzival agent and rated it 38 of 50 against 18, while noting that Parzival's GPU training and swarm collaboration are worth borrowing."),
);

children.push(
  H1("Decisions and tasks waiting for you"),
  P("The Euler paper is the most pressing. Please read it through as its author, because its statement on the use of AI tools says that you revised it; then obtain an endorsement for the math.NT category and upload Alesso_Euler_Elliptic_AI_Lab_arXiv.zip, using the title, abstract and comments in the submission guide. The errors you saw in TeXstudio came only from the missing figures folder. The note to Drs. Shi, Ceyhan and Billor is ready to send with the two full reports attached, and a covering email can be drafted on request. A screenshot of the live autoresearch leaderboard would confirm or correct Parzival's reported sixth place."),
  P("The technical tasks are, in rough order of value: merge the five branches into main and find a way to bring the agents' ledgers out of the sandboxes, where pushes are blocked; add a GPU program on Modal, ideally Karpathy's benchmark run under Artemis rules with a sealed test; add a memory shared across runs; complete the remaining parts of the UN-CCD work, namely the Modal sweep of Project 1, the RK-CCD and KS-CCD variants and Projects 3 to 6; and finish the website with a custom domain, a rebuild with the site address, and the CRON_SECRET setting."),
);

children.push(
  H1("Rules and lessons to carry forward"),
  P("Your standing preferences hold: documents as well-edited Word files in narrative prose without bullets or em dashes, code in complete Python files, no invented data, a choice of open and closed models when building with LLMs, and a plain statement when an answer is not known. Secrets stay in .env files, Modal secrets and Vercel settings and are never pasted into a chat; run transcripts can contain the Anthropic key, which is visible in sandbox process lists, so they stay private. Your gmail address stays out of public documents, and the paper uses alesso@alum.mit.edu. The authors' UN-CCD code carries no licence, so it is cloned at run time and never copied into the repository."),
  P("A few lessons cost time and are worth remembering. Claude's cloud workspace shuts down when idle and kills background jobs, so long computations must be watched while they run. Windows line-ending conversion once broke the data fingerprints, which a .gitattributes rule now prevents. arXiv now runs BibTeX itself, advises against the \\pdfoutput setting and limits abstracts to 1,920 characters. The Word documents are built from the content files in docs/source together with guide_helpers.js."),
);

const doc = new Document({
  creator: "H. P. Alesso", title: "Artemis Handoff Report",
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
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync("../Artemis_Handoff_Report_2026-10-19.docx", buf); console.log("written"); });
