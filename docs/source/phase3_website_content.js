// Content for "Artemis Phase 3: The Public Website". Appended to guide_helpers.js at build time.
const children = [];
const SITE = "https://artemis-ten-blond.vercel.app";

children.push(
  new Paragraph({ spacing: { before: 1400, after: 120 }, children: [new TextRun({ text: "ARTEMIS", font: HEAD_FONT, size: 22, bold: true, color: TEAL, characterSpacing: 120 })] }),
  new Paragraph({ spacing: { after: 200 }, children: [new TextRun({ text: "Phase 3: The Public Website", font: HEAD_FONT, size: 52, bold: true, color: INK })] }),
  new Paragraph({ spacing: { after: 600 }, children: [new TextRun({ text: "What is live, how it was tested, how to move it to your own domain, and whether the first result is worth showing the judges", font: BODY_FONT, size: 28, italics: true, color: MUTED })] }),
  new Paragraph({
    border: { top: { style: BorderStyle.SINGLE, size: 6, color: NAVY, space: 8 } },
    spacing: { after: 80 }, children: [new TextRun({ text: "Live at " + SITE + "  ·  Repository github.com/alessoh/artemis", font: HEAD_FONT, size: 20, color: INK })],
  }),
  new Paragraph({ spacing: { after: 80 }, children: [new TextRun({ text: "Saturday, October 3, 2026", font: HEAD_FONT, size: 20, color: MUTED })] }),
  new Paragraph({ spacing: { before: 1000 }, children: runs("This document closes Phase 3. It describes the website as it now stands on Vercel, the tests it passed, the work that remains before it would earn a top design grade, the three steps needed to move it to your own domain, and a frank answer to your question about whether the Phase 2 result is noteworthy for the hackathon. It ends with a proposal for the more detailed test you mentioned.", { size: 21, color: MUTED }) }),
  new Paragraph({ children: [new PageBreak()] }),
);

children.push(
  H1("1. The short version"),
  P("The Artemis website is live in light mode, with every page, link and button tested against the production deployment. A visitor sees a short menu of three words and one button: Results, Method, About, and Start an investigation. The home page leads with the first result in plain language, the flagship report sits one click away, and anyone holding the access code can start a run and watch the agents work in real time. Every finished run is written to the Neon database and published on the Results page, so nothing is lost when a browser closes."),
  P("Search engines and AI assistants are both catered for. Each public page carries a canonical address, a description, social preview tags with an image, and structured data that tells a crawler what the page is: an organization, a report, two datasets, a set of frequently asked questions, and a technical article. The site also publishes a sitemap, a robots file that welcomes AI crawlers while keeping them out of the API, and the llms.txt summary that assistants increasingly read first."),
  Pull("The site is ready for a custom domain today. The only steps left are yours: add the domain in Vercel, rebuild with one command so every link points to it, and push."),
);

children.push(
  H1("2. What a visitor sees"),
  P("The home page opens with a single sentence about what Artemis is, followed by the first result told as a story a non-specialist can follow: on data the agents had never seen, their method found every excellent solar absorber in 8 expensive calculations, where the textbook rule needed 20 and random picking about 344. Beside it a crystal lattice, drawn in Three.js and loaded only when it comes into view, turns slowly and can be dragged. Further down, a strip chart shows the later robustness check across twenty pools, followed by the five steps of a run and four reasons the numbers can be trusted."),
  Img("../figures/phase3_home.png", 600, 375),
  Caption("The home page at desktop width, captured from the same build that runs in production."),
  P("The flagship report is the heart of the site. It sets out the question, the held-out test, the robustness check with its caveats stated openly, the nineteen trials the agents ran and the four they kept, the fifteen materials worth computing next, and the lab's own report reproduced in full. A sidebar of contents follows the reader on wide screens and steps aside on narrower ones so the text keeps its width."),
  Img("../figures/phase3_report.png", 600, 375),
  Caption("The opening of the flagship report on solar absorbers."),
  P("The Lab page offers two choices. The first asks the Compiler to turn a visitor's own question into a testable experiment, which takes a few minutes and is the right demonstration for judges. The second repeats the full solar program, which takes one to three hours. A progress strip shows the run moving from sandbox to agents to saving to published, and the lead agent's messages appear as it writes them. On a phone the menu folds into a single button, and the long tables become cards so nothing has to be scrolled sideways."),
  Img("../figures/phase3_phone_menu.png", 200, 433),
  Caption("The menu on a phone, opened."),
);

children.push(
  H1("3. How the site was tested"),
  P("I tested the site in three ways. A Playwright suite in the repository, scripts/test_site.py, opens every page at desktop and phone widths, follows every internal link, presses every button, checks the menu, the chart and the tables, and then starts a complete run against a scripted stand-in for the Omnigent server, following it through to a saved and published report. Its final pass recorded 249 checks with none failing. Separately, I fetched every page of the live production deployment and confirmed each returned the right content, the right search-engine instructions and the security headers, that unknown pages return a proper 404 and unknown API addresses a JSON error, and that the status endpoint reports the Omnigent server, its credentials and the database as connected. Finally, I checked all twenty outside links. Eighteen open normally. The two journal links at the American Chemical Society and figshare refuse automated visitors, but their DOIs resolve correctly and they open in an ordinary browser."),
  P("Two faults surfaced during the live check and are fixed in this release. The production 404 page had fallen back to a bare placeholder because Vercel does not package the static folder with the Python function, so the API now carries its own copy of the page. The stylesheet also asked for an italic font file that was never shipped, which caused a harmless but untidy error on every page, and that request is gone."),
  P("Two independent reviewers also judged the work. An auditor checked search and assistant readiness and the accuracy of every claim. It scored search optimization 9 out of 10 and assistant optimization 8.5, and its accuracy findings were all corrected: the copy now leads with the held-out result, labels the twenty-pool check as a later analysis of a rebuilt model, calls the comparison the textbook rule rather than the best rule, and no longer describes the materials as non-toxic, because the pool can include beryllium and nickel. A deliberately harsh design critic scored the site 5.5 on its first look and 8.3 on its last. Its verdict was that the site is one it would put in front of judges, but not yet top grade. The two gaps it named were a hero that could belong to many science sites and a chart that informs without inviting play. I report that verdict as it was given rather than claim a grade the site has not earned."),
  table([3200, 1500, 4660], ["Check", "Result", "Notes"], [
    ["Automated page, link and run tests", "249 passed, 0 failed", "Desktop and phone; full run through to a saved report"],
    ["Live production pages", "All correct", "Clean addresses, 404 page, API errors, status all connected"],
    ["Outside links", "20 of 20 resolve", "Two publishers block robots; their DOIs resolve"],
    ["Search optimization (auditor)", "9 of 10", "Canonicals, previews, structured data, sitemap"],
    ["Assistant optimization (auditor)", "8.5 of 10", "llms.txt, llms-full.txt, FAQ data, open robots file"],
    ["Visual design (harsh critic)", "8.3 of 10", "Presentable to judges; not yet top grade"],
  ]),
  Caption("Test and review results for the Phase 3 release."),
);

children.push(
  H1("4. How results are saved"),
  P("When a run starts, the website writes a row for it in the artemis.runs table of the Neon database. While the visitor watches, the website relays the agents' messages from Omnigent. When the lead agent signals that it has finished, the website saves the final report and the lead's messages, gives the run a title, and closes the agent's sandbox. If the visitor closes the browser before that moment, a Vercel cron job that runs every fifteen minutes finds the unfinished run, saves its report when it is ready, and marks it as failed if the sandbox has disappeared or the run has gone on longer than eight hours. Saved runs appear on the Results page and each has its own page. The flagship solar report is part of the site itself and does not depend on the database at all."),
  P("At most two runs may be active at once, and starting one requires the access code, because every run spends money on Claude and Modal. Reading is open to everyone."),
);

children.push(
  H1("5. Moving to your own domain"),
  P("The site currently lives at " + SITE + ", and every canonical link, the sitemap and the llms.txt file name that address. Moving to your own domain takes three steps. First, open the artemis project in Vercel, choose Settings and then Domains, add your domain, and copy the DNS records Vercel shows into your domain registrar; Vercel issues the security certificate on its own once the records are in place. Second, in the Anaconda PowerShell Prompt, from the artemis folder, rebuild the site with your address in place of the example and send it to GitHub:"),
  P("python scripts/build_site.py --site-url https://your-domain.com", { indent: { left: 540 } }),
  P("git add -A, then git commit -m \"Point the site at its own domain\", then git push", { indent: { left: 540 } }),
  P("Vercel redeploys within about a minute of the push. Third, I recommend adding one more environment variable in Vercel under Settings and Environment Variables: CRON_SECRET, set to any long random phrase you choose and type only there. When it is present, Vercel's cron job sends it and nobody else can trigger the sync. Redeploy once after adding it. None of these steps needs you to paste a key or password into our conversation."),
);

children.push(
  H1("6. Was the Phase 2 result noteworthy for the hackathon?"),
  P("Yes, for the right reason, and it is worth being precise about which reason that is. The strongest thing Artemis can show the judges is not the size of the speed-up. It is that a team of AI agents ran a real research loop on real public data for three hours without human help, and did it honestly. The rules were written down before the first experiment. The scoring code and data were frozen and fingerprinted. A separate Skeptic agent rejected the single highest-scoring trial of the whole run as a fluke of the small practice set. The held-out test was run exactly once. Afterwards the method was rebuilt from the report alone and matched the lab's practice score exactly. Challenge 03 asks for an agentic lab for scientific discovery, and most entrants will show agents that produce plausible text. Very few will show agents that refuse their own best-looking result."),
  P("The numbers themselves are respectable and honestly framed. On the held-out test the method needed 8 calculations where the textbook rule needed 20 and random picking about 344. Because four excellent materials is a thin basis, the later check across twenty overlapping pools matters more: there the rebuilt method needed a median of 14.5 calculations against 26 for the corrected-gap rule, 47.5 for the textbook rule and about 1,161 for random order, and it beat the textbook rule in all twenty pools and the corrected-gap rule in nineteen. The agents also recovered a piece of real physics on their own, that the useful band gap for these cheap DFT values sits near 0.6 to 0.7 eV rather than at the textbook 1.34 eV, because this method underestimates gaps."),
  P("What it is not is a discovery, and the site says so plainly. The efficiency values are computed, not measured. Machine-learning screening of this very quantity in JARVIS was published by Choudhary and colleagues in 2019, so a judge who knows the field will see the method as a well-run instance of a known approach rather than a new one. The fifteen recommended materials have not yet been checked by the expensive calculation. I would therefore pitch Artemis as a trustworthy autonomous lab whose first run produced a verified, reproducible speed-up and a public list of what to compute next, and I would not pitch it as having found a new solar material."),
);

children.push(
  H1("7. A more detailed test, if time allows"),
  P("The most persuasive next test is prospective, meaning it checks predictions the lab made before the answers were known. The data snapshot Artemis used is the JARVIS-DFT release of August 2021. JARVIS has published newer releases since then, and if any of the fifteen shortlisted materials, or others from the unlabeled pool, have since received an efficiency value, we can score the lab's ranking against those new values without the lab ever having seen them. A hit rate well above the pool's base rate would be the strongest evidence Artemis can offer short of a laboratory. I have not yet confirmed how many of the shortlisted materials the newer release covers, so the first step is to download it on Modal, as we did for the original snapshot, and count the overlap before promising a result."),
  P("Two cheaper improvements would sit alongside it. The first is to add your Materials Project key, which the scripts already support through python scripts/make_secrets.py materials-project, so each recommendation can be cross-checked for stability against a second, independent database. The second is to tighten the keep rule so that a new idea must beat the current best on the practice set and also in cross-validation on the training data before it is kept, which is what the Skeptic did by judgment in the first run. Together these would cost a few dollars in computing and an afternoon of the lab's time, and I can prepare the runbook whenever you want to proceed."),
);

children.push(
  H1("Sources"),
  source("Artemis website", SITE),
  source("Artemis repository", "https://github.com/alessoh/artemis"),
  source("Phase 2 results document", "https://github.com/alessoh/artemis/blob/main/docs/Artemis_Phase2_Results.docx"),
  source("SLME screening in JARVIS, Choudhary et al., Chem. Mater. 31, 5900 (2019)", "https://doi.org/10.1021/acs.chemmater.9b02166"),
  source("JARVIS-Leaderboard, Choudhary et al., npj Computational Materials 10, 93 (2024)", "https://doi.org/10.1038/s41524-024-01259-w"),
  source("llms.txt proposal", "https://llmstxt.org"),
);

const doc = new Document({
  creator: "Claude",
  title: "Artemis Phase 3: The Public Website",
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
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "Artemis  ·  Phase 3 Website", font: HEAD_FONT, size: 16, color: MUTED })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: HEAD_FONT, size: 16, color: MUTED })] })] }) },
    children,
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync("Artemis_Phase3_Website.docx", buf);
  console.log("written");
});
