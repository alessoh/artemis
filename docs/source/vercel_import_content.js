// Content for "How to Import Artemis into Vercel". Appended to guide_helpers.js at build time.
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
const Step = (n, title) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(`Step ${n}. ${title}`)] });

const children = [];

children.push(
  new Paragraph({ spacing: { before: 1400, after: 120 }, children: [new TextRun({ text: "ARTEMIS", font: HEAD_FONT, size: 22, bold: true, color: TEAL, characterSpacing: 120 })] }),
  new Paragraph({ spacing: { after: 200 }, children: [new TextRun({ text: "How to Import Artemis into Vercel", font: HEAD_FONT, size: 52, bold: true, color: INK })] }),
  new Paragraph({ spacing: { after: 600 }, children: [new TextRun({ text: "A click-by-click guide to putting the alessoh/artemis repository on the web", font: BODY_FONT, size: 28, italics: true, color: MUTED })] }),
  new Paragraph({
    border: { top: { style: BorderStyle.SINGLE, size: 6, color: NAVY, space: 8 } },
    spacing: { after: 80 }, children: [new TextRun({ text: "Companion to the Phase 1 Runbook, step 7", font: HEAD_FONT, size: 20, color: INK })],
  }),
  new Paragraph({ spacing: { after: 80 }, children: [new TextRun({ text: "Saturday, October 3, 2026", font: HEAD_FONT, size: 20, color: MUTED })] }),
  new Paragraph({ children: [new PageBreak()] }),
);

children.push(
  H1("1. What importing does"),
  P("Importing tells Vercel to watch your GitHub repository. Vercel copies the code, builds it, and gives the result a public web address. From then on, every time new code is pushed to the repository's main branch, Vercel rebuilds and updates the site on its own, so you only do this once. The repository is named **alessoh/artemis**, with an h at the end of alessoh, because it lives under your GitHub account alessoh."),
  P("One honest note before you start: Vercel occasionally renames buttons and rearranges its screens. The steps below describe the standard import flow, and if a label on your screen differs slightly, look for the nearest equivalent. If you get stuck, tell me what the screen says and I will point you to the right place."),
);

children.push(
  H1("2. Before you start"),
  P("You need to be signed in to Vercel with the account that owns the team called alessoh's projects, and your Vercel account needs to be connected to your GitHub account alessoh. If you have deployed anything from GitHub to Vercel before, that connection already exists. The repository is public, so Vercel can read it without extra permissions once the GitHub connection is in place."),
  P("You can import the project before or after the Modal steps in the runbook. If you import first, the site will load but will report that the relay is not configured, because the environment variables are not filled in yet. That is expected and harmless, and section 4 shows how to add them later."),
);

children.push(
  H1("3. The steps"),
  Step(1, "Open your Vercel dashboard"),
  P("Go to vercel.com/alessohs-projects in your browser. You should see the dashboard for your team, alessoh's projects, with any existing projects listed."),
  Step(2, "Start a new project"),
  P("Near the top right of the dashboard, click the button labeled Add New, and in the small menu that opens, choose Project. Vercel opens a page titled something like Let's build something new, with a section called Import Git Repository."),
  Step(3, "Find the artemis repository"),
  P("In the Import Git Repository section, make sure the account shown at the top of the list is alessoh. You can type artemis into the search box to find it quickly. If artemis does not appear, Vercel's GitHub app has not been given access to it yet. Look for a link beneath the list called Adjust GitHub App Permissions or Configure GitHub App. Clicking it opens a GitHub page; choose your alessoh account, find the section named Repository access, either select All repositories or pick artemis from the list, and click Save. GitHub sends you back to Vercel, and artemis now appears in the list."),
  Step(4, "Click Import"),
  P("Click the Import button on the artemis row. Vercel opens the Configure Project page, which holds a few settings and a Deploy button at the bottom."),
  Step(5, "Check the project settings"),
  P("Four settings appear on this page, and only one may need your attention. The Project Name should read artemis; keep it, because it becomes part of your web address. The team, sometimes shown as Vercel Team or Scope, should be alessoh's projects. The Framework Preset should show FastAPI, which Vercel detects from the app.py and requirements.txt files in the repository; if it shows Other instead, open the dropdown and choose FastAPI. Leave the Root Directory as ./ and leave Build and Output Settings exactly as they are."),
  Step(6, "Add the environment variables, or skip for now"),
  P("Click Environment Variables to expand that section. Each variable has a Key box for the name and a Value box for the value, plus an Add button for each new row. Artemis needs the four variables below. If you have already run step 3 of the runbook, which creates your .env file, the following command prints the exact values to copy, one per line in the form NAME=value."),
  Code(["python scripts/make_secrets.py vercel"]),
  table([3900, 1000, 4460],
    ["Key", "Secret?", "What it is"],
    [
      ["OMNIGENT_URL", "No", "The Omnigent server's address on Modal"],
      ["OMNIGENT_MACHINE_CLIENT_ID", "No", "The name the website uses to log in to Omnigent (artemis-relay)"],
      ["OMNIGENT_MACHINE_CLIENT_SECRET", "Yes", "The website's password for Omnigent"],
      ["ARTEMIS_ACCESS_CODE", "Yes", "The code a visitor types before the site starts a lab session"],
    ]),
  Spacer(),
  P("Paste each name into a Key box and its value into the matching Value box, adding a row for each. Copy the values exactly, with no spaces before or after. If you have not created your .env file yet, simply skip this step; nothing breaks, and you will add the variables later."),
  Step(7, "Deploy"),
  P("Click Deploy. Vercel installs the Python libraries and builds the site, which usually takes one to two minutes; you can watch the build log scroll by. When it finishes, Vercel shows a congratulations screen with a small preview of the page. Click Continue to Dashboard."),
  Step(8, "Find your web address and check the page"),
  P("On the project's dashboard page, look for the Domains entry, which lists the production address, usually artemis followed by a short suffix and then .vercel.app. That production address is the one to use; the longer addresses listed under individual deployments are snapshots of particular builds. Open the production address. You should see the Artemis lab connection check page with its five-station signal path. The Website station should turn green right away. The Omnigent server station will show a problem until the environment variables are added and the Modal server from the runbook is running, which is exactly what we expect at this stage."),
);

children.push(
  H1("4. Adding or changing the environment variables later"),
  P("Open the artemis project in your Vercel dashboard and click Settings along the top, then choose Environment Variables in the left-hand menu. Add each of the four variables from the table above, leaving all three environments ticked (Production, Preview, and Development) and marking the two secret ones as Sensitive if Vercel offers that option. Click Save after each one."),
  P("Environment variables only reach new builds, so you must redeploy once afterwards. Click the Deployments tab, find the deployment at the top of the list, open the three-dot menu at the right of its row, choose Redeploy, and confirm. After a minute or two, reload your production address and the Omnigent server station should turn green, provided the Modal server is running."),
);

children.push(
  H1("5. Two things that can trip you up"),
  P("**A Vercel login screen instead of the Artemis page.** Vercel can protect deployments so that only members of your team can open them, a feature called Deployment Protection with Vercel Authentication. Depending on your team's defaults, new projects may protect preview addresses, and occasionally production ones too. If opening your production address shows a Vercel sign-in page rather than the Artemis page, go to the project's Settings, open Deployment Protection, and turn off Vercel Authentication, or limit it to preview deployments only. Artemis already guards its lab with its own access code, so the page itself is safe to leave public."),
  P("**A failed build.** If the deployment shows Error instead of Ready, click on it, open the Build Logs, and copy the last twenty or so lines into our chat. The logs contain no secrets, and I can usually tell from them exactly what went wrong."),
);

children.push(
  H1("6. What to send me"),
  P("Once the site is up, send me its production address, which is public and safe to share. With that address I can run the website check against it from my side whenever the Modal server is live, and the address goes into the smoke test command in step 8 of the runbook."),
);

const doc = new Document({
  creator: "Claude",
  title: "How to Import Artemis into Vercel",
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
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "Artemis  ·  Importing into Vercel", font: HEAD_FONT, size: 16, color: MUTED })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: HEAD_FONT, size: 16, color: MUTED })] })] }) },
    children,
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync("Artemis_Vercel_Import_Guide.docx", buf);
  console.log("written");
});
