// Content for "Euler's Identity paper: review and arXiv submission guide". Appended to guide_helpers.js at build time.
const children = [];
const ABSTRACT = fs.readFileSync("/home/claude/paper2/arxiv_meta/abstract.txt", "utf8").trim();
const Code = (text) => new Paragraph({
  spacing: { before: 40, after: 40 }, indent: { left: 360 },
  children: [new TextRun({ text, font: "Consolas", size: 18, color: INK })],
});

children.push(
  new Paragraph({ spacing: { before: 600, after: 120 }, children: [new TextRun({ text: "ARXIV SUBMISSION", font: HEAD_FONT, size: 22, bold: true, color: TEAL, characterSpacing: 120 })] }),
  new Paragraph({ spacing: { after: 160 }, children: [new TextRun({ text: "Euler's Identity, Elliptic Curves and an AI Laboratory: Review and Submission Guide", font: HEAD_FONT, size: 36, bold: true, color: INK })] }),
  new Paragraph({ spacing: { after: 400 }, children: [new TextRun({ text: "What went wrong in TeXstudio, what was checked, and how to submit the paper to arXiv", font: BODY_FONT, size: 24, italics: true, color: MUTED })] }),
);

children.push(
  H1("The problem in TeXstudio"),
  P("The three errors in your screenshot all say the same thing: pdfLaTeX could not find figures/fig_murmurations.pdf, figures/fig_loop.pdf and figures/fig_partB_test.pdf. The paper draws its three plots from a subfolder called figures that must sit next to the .tex file. Your folder C:\\MyAlesso\\CurriculumVitae\\papers holds the .tex file but not that subfolder, so LaTeX replaced each plot with an empty box (its \"draft setting\"). The line numbers in the errors, 173, 208 and 230, are exactly the lines of the three \\includegraphics commands, which confirms that the text itself is fine. The two \"Underfull \\vbox\" notes are harmless remarks about page breaks and do not need fixing."),
  P("The fix is to keep the whole package together. Unzip Alesso_Euler_Elliptic_AI_Lab_arXiv.zip into an empty folder, open the .tex file from that folder in TeXstudio and compile; the figures folder will then be beside it and all three plots will appear. If you have edited the .tex file on your computer since 8 October, keep your edited file and simply copy the figures folder from the zip next to it."),
);

children.push(
  H1("What was checked"),
  P("I compiled the package from a clean copy exactly as arXiv will, with pdfLaTeX and no other files. It builds without errors or warnings to 13 pages, all fonts are embedded, and the three figures, the TikZ diagram and the five tables appear where they should. The bibliography is written into the .tex file itself, so arXiv has nothing extra to compile and the reference list will come out exactly as it does on your computer; refs.bib is therefore not required and is left out of the package. The ancillary folder anc holds the numerical check script, which arXiv publishes beside the paper as a supplementary file; it contains no keys or personal data."),
  P("Every number in the paper was checked against the replication record on the langlands-lab branch, including the correlation of 0.5313 with interval 0.4605 to 0.5944, the AUCs of 0.522 and 0.543 with z of 8.6 and 15.1 on 775,454 pairs, and the positive control of 0.964; all agree. I also re-derived the mathematical identities that are easy to get wrong, among them the formula for zeta at even integers, the sign of the quadratic Gauss sum, the root number formula w(E) equal to minus the product of the local signs, and the rule that a self-dual root number squares to the central character at minus one; all are stated correctly. The links to Artemis, Omnigent and Karpathy's autoresearch point to real public repositories, and Artemis carries an MIT licence, so calling it open source is accurate."),
  P("Two small changes were made to the copy in the package. The reference to Isaacson's biography printed its title as \"Elon musk\" and now reads \"Elon Musk\". In the section on numerical checks a sentence ran straight on from the end of a table; it now starts its own paragraph. Nothing else in the text was changed. arXiv recognises pdfLaTeX papers automatically, so no setting is needed for that."),
);

children.push(
  H1("Points for you to decide before submitting"),
  P("The statement on the use of AI tools ends by saying that the author revised the manuscript and takes full responsibility for its content. arXiv requires that responsibility to rest with the human author, so please read the paper through as its author before submitting, and change the sentence if it does not describe what you did. The paper will also show your address alesso@alum.mit.edu publicly, which you may want to confirm."),
  P("The natural primary category is math.NT (Number Theory), with cs.AI (Artificial Intelligence) as a cross-list. If you have not posted to math.NT before, arXiv will ask for an endorsement from an established author in that category before the paper is announced; the submission can be prepared now and will wait for the endorsement. Moderators in mathematics sometimes reclassify papers whose main contribution is computational or expository, so the cross-list is useful. For the licence, CC BY 4.0 is the most open common choice; the arXiv perpetual non-exclusive licence keeps the most rights with you and leaves you freest to publish the paper in a journal later."),
  P("On the content, a referee in number theory is likely to ask two things. The first is whether Section 2, which the paper itself calls a guided tour with no new mathematics, is too long relative to the experiment; the paper's own framing answers this honestly, but you could shorten it if a journal asks. The second is the novelty of Part B, where the paper already says that a specialist literature search should precede any claim; that caution is right and should stay."),
);

children.push(
  H1("How to submit"),
  P("Sign in at arxiv.org/user and choose Start New Submission. On the first page confirm that you are the author, choose the licence, and pick math.NT as the archive and category. On the upload page, upload the single file Alesso_Euler_Elliptic_AI_Lab_arXiv.zip; arXiv unpacks it and keeps the folders. Then choose Continue: Process Files. arXiv compiles the paper and shows you its own PDF, which you should open and check page by page, especially that the three plots appear. If arXiv reports an error at this stage, copy its log and send it to me."),
  P("On the metadata page, enter the title, author and abstract below exactly as given. The abstract uses arXiv's math notation between dollar signs and is 1,729 characters long, under arXiv's limit of 1,920. Add math.NT as primary and cs.AI as cross-list, fill in the comments line, and leave the journal reference and DOI empty. The MSC classes are optional but help readers find the paper. After a final preview, submit. Papers submitted before 14:00 US Eastern time on a weekday are normally announced that evening, once the endorsement is in place."),
  new Paragraph({ spacing: { before: 200, after: 60 }, children: [new TextRun({ text: "Title", font: HEAD_FONT, bold: true, size: 20, color: NAVY })] }),
  Code("Euler's Identity, Elliptic Curves and an AI Laboratory"),
  new Paragraph({ spacing: { before: 160, after: 60 }, children: [new TextRun({ text: "Authors", font: HEAD_FONT, bold: true, size: 20, color: NAVY })] }),
  Code("H. P. Alesso"),
  new Paragraph({ spacing: { before: 160, after: 60 }, children: [new TextRun({ text: "Comments", font: HEAD_FONT, bold: true, size: 20, color: NAVY })] }),
  Code("13 pages, 4 figures, 5 tables. Code, data and replication: https://github.com/alessoh/artemis (branch langlands-lab)"),
  new Paragraph({ spacing: { before: 160, after: 60 }, children: [new TextRun({ text: "Categories", font: HEAD_FONT, bold: true, size: 20, color: NAVY })] }),
  Code("Primary: math.NT    Cross-list: cs.AI"),
  new Paragraph({ spacing: { before: 160, after: 60 }, children: [new TextRun({ text: "MSC classes (optional)", font: HEAD_FONT, bold: true, size: 20, color: NAVY })] }),
  Code("11G05, 11G40, 11F80"),
  new Paragraph({ spacing: { before: 160, after: 60 }, children: [new TextRun({ text: "Abstract", font: HEAD_FONT, bold: true, size: 20, color: NAVY })] }),
  Code(ABSTRACT),
);

children.push(
  H1("Files"),
  P("Alesso_Euler_Elliptic_AI_Lab_arXiv.zip is the file to upload; it contains the .tex file, the figures folder with three PDF plots, and the anc folder with the check script. Alesso_Euler_Elliptic_AI_Lab_arXiv_preview.pdf is the paper as it compiles from that zip, for comparison with what arXiv produces. The same abstract is also provided as a plain text file, arxiv_abstract.txt, for copying into the form."),
);

children.push(
  H1("Sources"),
  source("arXiv help: submitting TeX and LaTeX", "https://info.arxiv.org/help/submit_tex.html"),
  source("arXiv help: endorsement", "https://info.arxiv.org/help/endorsement.html"),
  source("arXiv help: licences", "https://info.arxiv.org/help/license/index.html"),
  source("arXiv help: preparing the abstract and metadata (1,920-character limit)", "https://info.arxiv.org/help/prep.html"),
  source("arXiv help: ancillary files", "https://info.arxiv.org/help/ancillary_files.html"),
);

const doc = new Document({
  creator: "H. P. Alesso", title: "Euler paper: review and arXiv submission guide",
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
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync("/home/claude/paper2/Euler_Paper_arXiv_Review_and_Submission_Guide.docx", buf); console.log("written"); });
