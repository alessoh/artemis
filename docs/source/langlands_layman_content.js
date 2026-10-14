// Content for "The Paper in Plain Words". Appended to guide_helpers.js at build time.
const children = [];

children.push(
  new Paragraph({ spacing: { before: 600, after: 120 }, children: [new TextRun({ text: "ARTEMIS", font: HEAD_FONT, size: 22, bold: true, color: TEAL, characterSpacing: 120 })] }),
  new Paragraph({ spacing: { after: 160 }, children: [new TextRun({ text: "Euler's Identity, Elliptic Curves and an AI Laboratory", font: HEAD_FONT, size: 40, bold: true, color: INK })] }),
  new Paragraph({ spacing: { after: 400 }, children: [new TextRun({ text: "A plain-language summary of the mathematics and the results", font: BODY_FONT, size: 26, italics: true, color: MUTED })] }),
);

children.push(
  H1("The idea behind the paper"),
  P("Euler's identity, e to the power iπ equals minus one, is often called the most beautiful equation in mathematics. One way to picture it is as a turn around a circle. Start at the number 1, walk halfway around a circle of radius one, and you arrive at minus one. Minus one is special because it is the only number other than 1 that gives 1 when you multiply it by itself. It is a switch with two positions, plus and minus."),
  P("Modern number theory is full of such switches. Mathematicians attach a sign, plus or minus, to many of the objects they study, and these signs often decide something important, such as whether an equation has finitely or infinitely many solutions. The paper's central claim is that a great many of these signs share one source. They can be traced to Euler's half turn, which appears whenever ordinary real numbers, the numbers on a ruler, enter a calculation. Number theorists call this the contribution of the \"real place\", as opposed to the contributions of the individual prime numbers 2, 3, 5, 7 and so on. The first half of the paper is a guided tour of where this one minus sign turns up across the vast web of ideas known as the Langlands program, and it ends with eight open questions that the tour suggests."),
);

children.push(
  H1("Where elliptic curves come in"),
  P("The tour becomes testable through elliptic curves, equations such as y² = x³ − x + 1. A central question about any such curve is how many solutions it has in fractions. Some curves have only a handful; others have infinitely many, generated from a few basic solutions. The number of independent basic solutions is called the rank of the curve. Deciding the rank is one of the great unsolved problems of mathematics, and it lies at the heart of the Birch and Swinnerton-Dyer conjecture, one of the Clay Institute's million-dollar problems."),
  P("Every elliptic curve carries a sign, plus or minus, that is predicted to tell whether its rank is even or odd. That sign is built from smaller signs, one for each of the curve's \"bad primes\", the primes where the equation breaks down. But there is an extra factor of minus one in the recipe, and that extra minus one is exactly Euler's half turn from the real place. The paper's first question exploits this. If you move from ordinary fractions to a slightly larger number system, here the numbers built from the square root of 5, there are two real places instead of one, so there are two half turns, and minus one times minus one is plus one. The extra sign should flip."),
  P("To see the flip, the paper uses a phenomenon discovered only in 2022 with the help of machine learning, called murmurations. Count how many solutions a curve has when arithmetic is done modulo a prime, as on a clock face, and average a suitably adjusted version of that count over many curves. As the prime grows, the averages rise and fall in a wave, like the shifting shape of a flock of starlings. The wave follows the curve's overall sign. So if the sign rule flips over the square root of 5, the murmuration wave there should line up with the product of the small signs, rather than with its opposite as it does over ordinary fractions."),
  P("The paper's second question is new. Curves of rank 0 and rank 2 have the same overall sign, because both ranks are even. Do their small signs, prime by prime, still differ in some systematic way, or is all the difference between them hidden elsewhere?"),
);

children.push(
  H1("Artemis, the AI laboratory"),
  P("To answer these questions, the paper uses Artemis, a laboratory we built in which a team of AI agents does the computational research. One agent searches the literature, one proposes ideas, several write and test experiments in parallel, a skeptic tries to knock down every apparent success, and a scribe writes the report. The agents are free to try ideas, but they cannot change how those ideas are judged. A frozen program, whose code and data are sealed with digital fingerprints, scores every experiment. The rules and the hypotheses were written down and published before the run, and a final set of data was locked away and used exactly once, at the very end."),
  P("These safeguards proved their worth before the run began. A separate AI agent, asked to try to break the system, discovered that the order in which curves are listed in the standard mathematical tables quietly reveals their rank. An agent that noticed this could have scored well without learning anything about mathematics. The leak was closed, and the paper reports it as a warning to anyone who uses AI on curated scientific data."),
);

children.push(
  H1("What the laboratory found"),
  P("The first question came out as theory predicts. For curves over the square root of 5, the murmuration wave lines up with the product of the small signs, the flip that the two real places require. The match with the wave over ordinary fractions had a correlation of 0.53, where zero would mean no relationship, and the uncertainty range stayed well clear of zero. This confirms known mathematics rather than discovering new mathematics, but it is a clean public demonstration of Euler's minus sign at work inside a pattern found only recently. There was also a surprise. The two waves agree for small primes but part company for large ones, which hints that over the larger number system the wave may run on a different scale. That is an open puzzle."),
  P("The second question produced a small but genuine discovery. Among curves that share the same conductor, a kind of address that fixes their bad primes, the small signs of rank 2 curves do differ from those of rank 0 curves. The difference is faint. A useful way to read the scores is this: pick a rank 2 curve and a rank 0 curve at the same address, show a rule only their signs, and ask it to guess which is which. Guessing at random is right half the time. The simple rule fixed in advance was right 52 percent of the time, and the rule the AI agents developed was right 54 percent of the time. For comparison, a rule allowed to look at those solution counts is right 96 percent of the time. Almost all of the difference between the two ranks therefore lies elsewhere, but the signs carry a real trace."),
  P("Small as it is, the effect is certain. It was measured on about 210,000 curves that no person or agent had examined before, and by standard statistical measures the chance of seeing it by luck is far below one in a million. The agents also found where the trace lives. A minus sign at a bad prime of 5 or more leans towards rank 2, while a minus sign at the primes 2 or 3 leans towards rank 0. A second clue, tied to the type of breakdown the curve has at a bad prime, looked promising but did not pass a strict check, so it remains a lead rather than a result."),
  P("Finally, the key results were checked independently. A separate AI session rebuilt the agents' final rule from their report, confirmed that it was identical to the one they submitted, and ran the final test again. Every number came out exactly the same. All the code and data are public."),
);

children.push(
  H1("What it means"),
  P("The paper does not prove a theorem or solve a famous problem. What it offers is a new way of seeing a familiar fact, a confirmation of that view in real data, and one small new observation about how the signs of elliptic curves relate to their ranks, with a clear list of next steps. The most promising of these is to test whether the effect is explained by the Tamagawa numbers, quantities that measure how badly a curve breaks at each bad prime and that appear in the Birch and Swinnerton-Dyer formula."),
  P("The paper also shows something about AI in science. The agents worked on their own, found a rule a mathematician can state in one sentence, and discarded clever models that did not hold up. Yet the most important moment of the project was the hidden leak that a second agent caught. The lesson is that the value of an AI laboratory lies less in how clever its agents are than in the fixed rules, sealed data and independent checks that keep them honest."),
);

const doc = new Document({
  creator: "Claude", title: "Euler's Identity, Elliptic Curves and an AI Laboratory: The Paper in Plain Words",
  styles: {
    default: { document: { run: { font: BODY_FONT, size: 22, color: INK } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 30, bold: true, font: HEAD_FONT, color: NAVY },
        paragraph: { spacing: { before: 360, after: 160 }, outlineLevel: 0, keepNext: true } },
    ],
  },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: HEAD_FONT, size: 16, color: MUTED })] })] }) },
    children,
  }],
});
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync("Artemis_Langlands_Plain_Summary.docx", buf); console.log("written"); });
