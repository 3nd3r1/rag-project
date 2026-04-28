import re
from datetime import date

from rich import box
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from llm_provider import create_llm, invoke_llm
from rag_pipeline import RAGPipeline
from vector_store import VectorStore


console = Console()


TEST_CASES = [
    {
        "question": "What is the sales trend over the 4-year period?",
        "truth": "Sales grew overall from $484,247.50 (2014) to $733,215.26 (2017). 2015 dipped slightly to $470,532.51 before rising to $609,205.60 in 2016 and peaking in 2017.",
        "criteria": [
            "Mentions all four years with sales figures",
            "Identifies the overall upward trend",
            "Notes a dip in one of the years",
        ],
    },
    {
        "question": "Which months show the highest sales? Is there seasonality?",
        "truth": "Sales peak in November ($352,461.07) and December ($325,293.50), with a secondary peak in September ($307,649.95). This suggests a strong end-of-year seasonality pattern.",
        "criteria": [
            "Identifies the peak months",
            "Mentions a seasonality pattern",
            "Provides actual dollar amounts",
        ],
    },
    {
        "question": "How has profit margin changed over time?",
        "truth": "Profit margin improved from 10.23% in 2014 to 13.10% in 2015, peaked at 13.43% in 2016, then declined slightly to 12.74% in 2017.",
        "criteria": [
            "Provides profit margin percentages for each year",
            "Identifies the peak year",
            "Notes the decline in the final year",
        ],
    },
    {
        "question": "Which product category generates the most revenue?",
        "truth": "Technology generates the most revenue at $836,154.03, followed by Furniture $741,999.80 and Office Supplies $719,047.03",
        "criteria": [
            "Identifies the top category with a dollar amount",
        ],
    },
    {
        "question": "What sub-categories have the highest profit margins?",
        "truth": "Top sub-categories by profit margin: Labels 44.42%, Paper 43.39%, Envelopes 42.27%, Copiers 37.20%, Fasteners 31.40%.",
        "criteria": [
            "Lists at least 3 sub-categories with profit margin percentages",
        ],
    },
    {
        "question": "Which products are frequently sold at a discount?",
        "truth": "The most discounted sub-categories by number of discounted transactions: Binders (1,186), Phones (578), Paper (513), Chairs (484), Furnishings (386).",
        "criteria": [
            "Identifies the most discounted sub-category",
            "Lists at least 3 sub-categories with discount counts",
        ],
    },
    {
        "question": "Which region has the best sales performance?",
        "truth": "The top sales regions are: 1. West $725,457.82, 2. East $678,781.24, 3. Central $501,239.89",
        "criteria": [
            "Identifies the top region with a dollar amount",
        ],
    },
    {
        "question": "Compare sales performance across different states.",
        "truth": "Top 5 states by total sales: California $457,687.63, New York $310,876.27, Texas $170,188.05, Washington $138,641.27, Pennsylvania $116,511.91.",
        "criteria": [
            "Identifies the top state by sales",
            "Compares at least 3 states with dollar amounts",
            "Mentions a low-performing or negative-profit state",
        ],
    },
    {
        "question": "Which cities are the top performers in terms of sales?",
        "truth": "Top 5 cities by sales: New York City $256,368.16, Los Angeles $175,851.34, Seattle $119,540.74, San Francisco $112,669.09, Philadelphia $109,077.01.",
        "criteria": [
            "Identifies the top city",
            "Lists at least 3 cities with sales figures",
        ],
    },
    {
        "question": "Compare Technology vs. Furniture sales trends over the years.",
        "truth": "Technology sales: 2014 $175,278.23, 2015 $162,780.81, 2016 $226,364.18, 2017 $271,730.81. Furniture sales: 2014 $157,192.85, 2015 $170,518.24, 2016 $198,901.44, 2017 $215,387.27. Technology leads in all years except 2015.",
        "criteria": [
            "Provides yearly sales for both categories",
            "Notes which category leads overall",
            "Mentions the year where the trailing category exceeded the other",
        ],
    },
    {
        "question": "How does the West region compare to the East in terms of profit?",
        "truth": "West region profit is $108,418.45 versus East region profit of $91,522.78. West outperforms East by $16,895.67.",
        "criteria": [
            "States profit figures for both regions",
            "Identifies which region outperforms the other",
        ],
    },
]


JUDGE_PROMPT = """\
You are evaluating a RAG system that answers questions about a sales dataset.
Judge only facts, ignore formatting and phrasing differences.

Question: {question}

Reference: {truth}

Criteria for a good answer:
{criteria_list}

RAG Answer: {rag_answer}

Score the answer considering both factual accuracy against the reference and the criteria:
5 - All facts correct and all criteria met.
4 - Most facts correct, only minor omissions.
3 - Some key facts correct but important information missing or wrong.
2 - Mostly incorrect or missing, with only minor correct elements.
1 - Completely wrong or not relevant answer.

Reply with:
SCORE: <integer 1-5>
EXPLANATION: <one sentence explaining the score>
"""


def judge(question: str, truth: str, criteria: list[str], rag_answer: str) -> tuple[int, str]:
    llm = create_llm()
    criteria_list = "\n".join(f"- {c}" for c in criteria) if criteria else "- N/A"
    prompt = JUDGE_PROMPT.format(
        question=question, truth=truth, rag_answer=rag_answer, criteria_list=criteria_list,
    )
    text = invoke_llm(llm, prompt)

    score_match = re.search(r"SCORE:\s*([1-5])", text)
    explanation_match = re.search(r"EXPLANATION:\s*(.+)", text)

    score = int(score_match.group(1)) if score_match else 0
    explanation = (
        explanation_match.group(1).strip() if explanation_match else text.strip()
    )

    return score, explanation


def write_report(results: list[dict], path: str):
    lines = [
        "# Report",
        f"**Date:** {date.today()}  ",
        "",
    ]

    scored = [r["score"] for r in results if r["score"] > 0]
    if scored:
        avg = sum(scored) / len(scored)
        lines += [
            "## Summary",
            f"- **Questions:** {len(results)}",
            f"- **Judged:** {len(scored)}",
            f"- **Average score:** {avg:.2f} / 5.00",
            f"- **Pass:** {sum(1 for s in scored if s >= 4)}",
            f"- **Fail:** {sum(1 for s in scored if s < 4)}",
            "",
        ]

    lines += [
        "## Results",
        "",
        "| # | Question | Score | Explanation |",
        "|---|----------|-------|-------------|",
    ]
    for i, r in enumerate(results, 1):
        score = f"{r['score']}/5" if r["score"] else "N/A"
        question = r["tc"]["question"].replace("|", "\\|")
        explanation = r["explanation"].replace("|", "\\|")
        lines.append(f"| {i} | {question} | {score} | {explanation} |")

    lines += ["", "## Details", ""]
    for i, r in enumerate(results, 1):
        lines += [
            f"### {i}. {r['tc']['question']}",
            "",
            f"**Truth:** {r['tc']['truth']}",
            "",
            f"**Criteria:**",
        ]
        for c in r["tc"].get("criteria", []):
            lines.append(f"- {c}")
        lines += [
            "",
            f"**RAG Answer:** {r['rag_answer']}",
            "",
            f"**Score:** {r['score']}/5 — {r['explanation']}",
            "",
        ]

    with open(path, "w") as f:
        f.write("\n".join(lines))


def run_evaluation(report_path: str | None = None):
    store = VectorStore()
    rag = RAGPipeline(store)

    results = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Running tests...", total=len(TEST_CASES))

        for i, tc in enumerate(TEST_CASES, 1):
            progress.update(task, description=f"{i}/{len(TEST_CASES)} {tc['question']}")

            rag_answer = rag.query(tc["question"])
            score, explanation = judge(
                question=tc["question"],
                truth=tc["truth"],
                criteria=tc.get("criteria", []),
                rag_answer=str(rag_answer),
            )
            results.append(
                {
                    "tc": tc,
                    "rag_answer": rag_answer,
                    "score": score,
                    "explanation": explanation,
                }
            )
            progress.advance(task)

    table = Table(box=box.ROUNDED, show_lines=True, title="Results")
    table.add_column("#", style="dim", width=3, justify="right")
    table.add_column("Question", min_width=36)
    table.add_column("RAG Answer", min_width=36)
    table.add_column("Score", width=7, justify="center")
    table.add_column("Explanation", min_width=36)

    for i, r in enumerate(results, 1):
        score = r["score"]
        color = "green" if score >= 4 else "yellow" if score >= 2 else "red"
        score_str = f"[{color}]{score}/5[/{color}]" if score else ""
        table.add_row(
            str(i), r["tc"]["question"], r["rag_answer"], score_str, r["explanation"]
        )

    console.print()
    console.print(table)

    scored = [r["score"] for r in results if r["score"] > 0]
    if scored:
        avg = sum(scored) / len(scored)
        console.print(
            f"\nAverage score: [blue]{avg:.2f} / 5.00[/blue]  ({len(scored)}/{len(results)} judged)\n"
        )

    if report_path:
        write_report(results, report_path)
        console.print(f"[green]✓[/green] Report saved to [bold]{report_path}[/bold]\n")
