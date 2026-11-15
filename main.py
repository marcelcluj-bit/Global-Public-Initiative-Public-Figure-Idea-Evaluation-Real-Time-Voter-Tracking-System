import os
import json
import datetime
import feedparser
from google import genai
from google.genai import types

# Configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
DATA_FILE = "data/proposals.json"
HTML_OUTPUT_FILE = "docs/index.html"

# Global News & Political RSS Feeds (Adaptable to any country or global figure)
GLOBAL_RSS_FEEDS = [
    "https://feeds.bbci.co.uk/news/politics/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml",
    "https://www.theguardian.com/politics/rss",
    "https://www.euronews.com/rss?format=mrss&level=theme&name=news"
]

MAX_ARTICLES_TO_SCAN = 15
MAX_NEW_PROPOSALS_PER_RUN = 3


def initialize_directories():
    os.makedirs("data", exist_ok=True)
    os.makedirs("docs", exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2)


def load_existing_proposals():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_proposals(proposals):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(proposals, f, indent=2, ensure_ascii=False)


def fetch_global_news(existing_urls):
    articles = []
    for feed_url in GLOBAL_RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:5]:
                link = entry.get("link", "")
                if link and link not in existing_urls:
                    articles.append({
                        "title": entry.get("title", "No Title"),
                        "summary": entry.get("summary", ""),
                        "link": link,
                        "published": entry.get("published", datetime.date.today().isoformat())
                    })
        except Exception as e:
            print(f"Warning: Could not parse feed {feed_url}: {e}")
    return articles[:MAX_ARTICLES_TO_SCAN]


def analyze_public_figure_idea(client, article):
    prompt = f"""
    You are an objective Global Political Analyst and Project Management AI.
    Analyze the following news item regarding a public figure or politician:

    Title: {article['title']}
    Summary: {article['summary']}
    Source URL: {article['link']}

    Task:
    1. Determine if this news item describes a specific policy idea, reform proposal, campaign promise, or public initiative announced, debated, implemented, or abandoned by a named public figure / politician anywhere in the world.
    2. If it does NOT involve a named public figure's idea or policy proposal, return strictly: {{"is_valid_proposal": false}}
    3. If it DOES involve a public figure's idea, generate a complete, objective Project Management & Voter Accountability Matrix in English.

    Respond ONLY with valid JSON using this exact schema:
    {{
        "is_valid_proposal": true,
        "public_figure": "Full Name of the Politician / Public Figure",
        "country_or_organization": "Country or International Body",
        "idea_title": "Concise, neutral title of the proposed policy or vision",
        "implementation_status": "Proposed | In Progress | Implemented | Abandoned / Contradicted",
        "status_justification": "1-2 sentences explaining the current real-world execution status of this idea.",
        "public_availability": "Open Public Blueprint | Closed Government / Party Initiative",
        "stakeholder_analysis": [
            {{"stakeholder": "Group/Entity", "role": "Role in proposal", "power_interest": "High/Medium/Low", "strategy": "Engagement or accountability strategy"}}
        ],
        "problem_tree": {{
            "core_problem": "Central problem the public figure claims to solve",
            "causes": ["Root cause 1", "Root cause 2", "Root cause 3"],
            "effects": ["Negative effect 1", "Negative effect 2", "Negative effect 3"]
        }},
        "objective_tree": {{
            "general_objective": "Main measurable goal of the proposal",
            "specific_objectives": ["Specific objective 1", "Specific objective 2", "Specific objective 3"],
            "expected_impact": "Long-term societal or economic impact if fulfilled"
        }},
        "swot_analysis": {{
            "strengths": ["Strength 1", "Strength 2"],
            "weaknesses": ["Weakness 1", "Weakness 2"],
            "opportunities": ["Opportunity 1", "Opportunity 2"],
            "threats": ["Threat 1", "Threat 2"]
        }},
        "ishikawa_fishbone": {{
            "legislative_barriers": "Legal or constitutional hurdles",
            "political_incentives": "Political alignment or opposition dynamics",
            "technological_operational_gaps": "Execution and infrastructure requirements",
            "cultural_civic_inertia": "Public adoption or societal resistance factors"
        }},
        "logical_framework": [
            {{"level": "Impact", "indicators": "Measurable KPI", "verification_sources": "Official audit/registry", "assumptions": "External condition"}},
            {{"level": "Outcome", "indicators": "Measurable KPI", "verification_sources": "Public data/report", "assumptions": "Key condition"}},
            {{"level": "Outputs", "indicators": "Deliverable count", "verification_sources": "Legislative/Executive record", "assumptions": "Resource availability"}}
        ],
        "activity_list_and_gantt": [
            {{"phase": "Phase 1 (Months 1-2)", "activity": "Policy drafting and legislative/institutional review", "responsible": "Initiator & Policy Team"}},
            {{"phase": "Phase 2 (Months 3-6)", "activity": "Pilot deployment and budget allocation", "responsible": "Executive Agency"}},
            {{"phase": "Phase 3 (Months 7-12)", "activity": "Full-scale rollout and public audit", "responsible": "Oversight Body"}}
        ],
        "estimated_budget_eur": [
            {{"category": "Policy Design & Legal Audit", "cost_eur": 25000, "notes": "Institutional research & compliance"}},
            {{"category": "Core Implementation & Operations", "cost_eur": 250000, "notes": "Estimated execution cost"}},
            {{"category": "Contingency & Oversight (10%)", "cost_eur": 27500, "notes": "Risk and audit reserve"}}
        ]
    }}
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2
            )
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Error calling Gemini API for '{article['title']}': {e}")
        return {"is_valid_proposal": False}


def get_status_badge_class(status):
    s = status.lower()
    if "implemented" in s:
        return "status-implemented"
    if "progress" in s:
        return "status-progress"
    if "abandoned" in s or "contradicted" in s:
        return "status-abandoned"
    return "status-proposed"


def render_static_website(proposals):
    last_updated = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    cards_html = ""

    for idx, item in enumerate(reversed(proposals)):
        proposal_id = f"prop_{len(proposals) - idx}"
        data = item["analysis"]
        total_budget = sum(b.get("cost_eur", 0) for b in data.get("estimated_budget_eur", []))
        status = data.get("implementation_status", "Proposed")
        status_class = get_status_badge_class(status)

        stakeholders_rows = "".join(
            f"<tr><td>{s['stakeholder']}</td><td>{s['role']}</td><td>{s['power_interest']}</td><td>{s['strategy']}</td></tr>"
            for s in data.get("stakeholder_analysis", [])
        )

        gantt_rows = "".join(
            f"<tr><td><strong>{g['phase']}</strong></td><td>{g['activity']}</td><td>{g['responsible']}</td></tr>"
            for g in data.get("activity_list_and_gantt", [])
        )

        logframe_rows = "".join(
            f"<tr><td><strong>{lf['level']}</strong></td><td>{lf['indicators']}</td><td>{lf['verification_sources']}</td><td>{lf['assumptions']}</td></tr>"
            for lf in data.get("logical_framework", [])
        )

        budget_rows = "".join(
            f"<tr><td>{b['category']}</td><td>{b['cost_eur']:,} EUR</td><td>{b['notes']}</td></tr>"
            for b in data.get("estimated_budget_eur", [])
        )

        causes_li = "".join(f"<li>{c}</li>" for c in data["problem_tree"]["causes"])
        effects_li = "".join(f"<li>{e}</li>" for e in data["problem_tree"]["effects"])
        spec_obj_li = "".join(f"<li>{o}</li>" for o in data["objective_tree"]["specific_objectives"])

        swot = data["swot_analysis"]
        ishikawa = data["ishikawa_fishbone"]

        cards_html += f"""
        <article class="case-card" id="{proposal_id}">
            <div class="case-header">
                <div>
                    <span class="badge-figure">{data.get('public_figure', 'Public Figure')} ({data.get('country_or_organization', 'Global')})</span>
                    <span class="badge-status {status_class}">Status: {status}</span>
                    <span class="badge-access">{data.get('public_availability', 'Publicly Tracked')}</span>
                </div>
                <span class="date">Logged: {item['date']}</span>
            </div>

            <h2>{data['idea_title']}</h2>
            <p class="status-note"><strong>Execution Audit:</strong> {data.get('status_justification', '')}</p>
            <p class="source-link">Reference Source: <a href="{item['source_url']}" target="_blank" rel="noopener">{item['original_title']}</a></p>

            <!-- Real-Time Voter Accountability Module (Vot in Timp) -->
            <div class="vot-in-timp-box">
                <div class="vot-header">
                    <h3>Vot în Timp — Real-Time Voter Vision Alignment</h3>
                    <span class="vot-subtitle">Do you judge that this leader is fulfilling their vision on this proposal?</span>
                </div>
                <div class="vot-controls">
                    <button class="btn-vote btn-yes" onclick="castVote('{proposal_id}', 'fulfills')">✔ Fulfills Vision (<span id="{proposal_id}-yes">0</span>)</button>
                    <button class="btn-vote btn-no" onclick="castVote('{proposal_id}', 'fails')">✖ Fails Vision (<span id="{proposal_id}-no">0</span>)</button>
                </div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" id="{proposal_id}-bar" style="width: 50%;"></div>
                </div>
                <p class="vot-stats" id="{proposal_id}-stats">Real-Time Alignment Score: 50% Fulfills / 50% Fails (Cast your vote above)</p>
            </div>

            <details>
                <summary>Inspect Full 8-Point Project Management Blueprint (Stakeholders, Trees, SWOT, Ishikawa, LogFrame, Gantt & Budget)</summary>
                <div class="matrix-content">
                    <h4>1. Stakeholder Analysis</h4>
                    <table>
                        <thead><tr><th>Stakeholder</th><th>Role</th><th>Power/Interest</th><th>Strategy</th></tr></thead>
                        <tbody>{stakeholders_rows}</tbody>
                    </table>

                    <div class="grid-2">
                        <div class="box">
                            <h4>2. Problem Tree</h4>
                            <p><strong>Core Problem:</strong> {data['problem_tree']['core_problem']}</p>
                            <p><strong>Root Causes:</strong></p><ul>{causes_li}</ul>
                            <p><strong>Effects:</strong></p><ul>{effects_li}</ul>
                        </div>
                        <div class="box">
                            <h4>3. Objective Tree</h4>
                            <p><strong>General Objective:</strong> {data['objective_tree']['general_objective']}</p>
                            <p><strong>Specific Objectives:</strong></p><ul>{spec_obj_li}</ul>
                            <p><strong>Expected Impact:</strong> {data['objective_tree']['expected_impact']}</p>
                        </div>
                    </div>

                    <h4>4. SWOT Analysis</h4>
                    <div class="grid-2">
                        <div class="box"><strong>Strengths:</strong><ul>{''.join(f'<li>{x}</li>' for x in swot['strengths'])}</ul></div>
                        <div class="box"><strong>Weaknesses:</strong><ul>{''.join(f'<li>{x}</li>' for x in swot['weaknesses'])}</ul></div>
                        <div class="box"><strong>Opportunities:</strong><ul>{''.join(f'<li>{x}</li>' for x in swot['opportunities'])}</ul></div>
                        <div class="box"><strong>Threats:</strong><ul>{''.join(f'<li>{x}</li>' for x in swot['threats'])}</ul></div>
                    </div>

                    <h4>5. Ishikawa (Fishbone) Execution Risk Analysis</h4>
                    <div class="grid-2">
                        <div class="box"><strong>Legislative Barriers:</strong> {ishikawa['legislative_barriers']}</div>
                        <div class="box"><strong>Political Incentives:</strong> {ishikawa['political_incentives']}</div>
                        <div class="box"><strong>Technological & Operational Gaps:</strong> {ishikawa['technological_operational_gaps']}</div>
                        <div class="box"><strong>Cultural & Civic Inertia:</strong> {ishikawa['cultural_civic_inertia']}</div>
                    </div>

                    <h4>6. Logical Framework Matrix (LogFrame)</h4>
                    <table>
                        <thead><tr><th>Hierarchy</th><th>Objectively Verifiable Indicators</th><th>Verification Sources</th><th>Assumptions</th></tr></thead>
                        <tbody>{logframe_rows}</tbody>
                    </table>

                    <h4>7. Activity Plan & Gantt Schedule</h4>
                    <table>
                        <thead><tr><th>Timeline / Phase</th><th>Activity</th><th>Responsible Unit</th></tr></thead>
                        <tbody>{gantt_rows}</tbody>
                    </table>

                    <h4>8. Estimated Project Budget (Total: {total_budget:,} EUR)</h4>
                    <table>
                        <thead><tr><th>Budget Category</th><th>Estimated Cost</th><th>Notes</th></tr></thead>
                        <tbody>{budget_rows}</tbody>
                    </table>
                </div>
            </details>
        </article>
        """

    if not cards_html:
        cards_html = "<p>No public figure proposals indexed yet. Run the pipeline to scan global political feeds.</p>"

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Global Politician Idea Tracker & Vot în Timp Accountability Portal</title>
    <style>
        :root {{
            --primary: #0f172a;
            --secondary: #1d4ed8;
            --bg: #f1f5f9;
            --card-bg: #ffffff;
            --text: #1e293b;
            --border: #cbd5e1;
        }}
        body {{ font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 0; line-height: 1.6; }}
        header {{ background: var(--primary); color: #fff; padding: 2.2rem 1rem; text-align: center; border-bottom: 4px solid #3b82f6; }}
        header h1 {{ margin: 0; font-size: 1.9rem; }}
        header p {{ margin: 0.5rem 0 0; opacity: 0.9; max-width: 750px; margin-inline: auto; }}
        .meta-bar {{ background: #e2e8f0; padding: 0.6rem 1rem; text-align: center; font-size: 0.875rem; }}
        main {{ max-width: 1100px; margin: 2rem auto; padding: 0 1rem; }}
        .case-card {{ background: var(--card-bg); border-radius: 8px; padding: 1.5rem; margin-bottom: 2rem; box-shadow: 0 2px 8px rgba(0,0,0,0.07); border-left: 6px solid var(--secondary); }}
        .case-header {{ display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.75rem; }}
        .badge-figure {{ background: var(--primary); color: #fff; padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.8rem; font-weight: 600; }}
        .badge-status {{ padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.8rem; font-weight: 600; color: #fff; }}
        .status-implemented {{ background: #16a34a; }}
        .status-progress {{ background: #2563eb; }}
        .status-proposed {{ background: #d97706; }}
        .status-abandoned {{ background: #dc2626; }}
        .badge-access {{ background: #e2e8f0; color: #334155; padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.8rem; font-weight: 500; }}
        .date {{ font-size: 0.85rem; color: #64748b; }}
        .status-note {{ background: #f8fafc; border-left: 3px solid #64748b; padding: 0.5rem 0.75rem; font-size: 0.92rem; }}
        .source-link {{ font-size: 0.9rem; color: #475569; }}
        .vot-in-timp-box {{ background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 1rem 1.25rem; margin: 1.25rem 0; }}
        .vot-header h3 {{ margin: 0; color: #1e3a8a; font-size: 1.1rem; }}
        .vot-subtitle {{ font-size: 0.88rem; color: #475569; }}
        .vot-controls {{ display: flex; gap: 1rem; margin: 0.85rem 0; flex-wrap: wrap; }}
        .btn-vote {{ border: none; padding: 0.55rem 1.1rem; border-radius: 6px; font-weight: 600; cursor: pointer; font-size: 0.9rem; transition: opacity 0.2s; }}
        .btn-vote:hover {{ opacity: 0.88; }}
        .btn-yes {{ background: #16a34a; color: #fff; }}
        .btn-no {{ background: #dc2626; color: #fff; }}
        .progress-bar-bg {{ width: 100%; height: 10px; background: #fca5a5; border-radius: 999px; overflow: hidden; }}
        .progress-bar-fill {{ height: 100%; background: #16a34a; transition: width 0.3s ease; }}
        .vot-stats {{ margin: 0.5rem 0 0; font-size: 0.85rem; font-weight: 600; color: #1e293b; }}
        details {{ margin-top: 1rem; border: 1px solid var(--border); border-radius: 6px; padding: 0.75rem; background: #f8fafc; }}
        summary {{ cursor: pointer; font-weight: 600; color: var(--secondary); }}
        .matrix-content {{ margin-top: 1rem; }}
        table {{ width: 100%; border-collapse: collapse; margin: 0.75rem 0 1.5rem; font-size: 0.9rem; background: #fff; }}
        th, td {{ border: 1px solid var(--border); padding: 0.6rem; text-align: left; vertical-align: top; }}
        th {{ background: #e2e8f0; }}
        .grid-2 {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }}
        .box {{ background: #fff; border: 1px solid var(--border); border-radius: 6px; padding: 1rem; }}
        footer {{ text-align: center; padding: 2rem 1rem; color: #64748b; font-size: 0.875rem; }}
    </style>
</head>
<body>
    <header>
        <h1>Global Politician Idea Tracker & Vot în Timp</h1>
        <p>Open-Source Project Management Audit of Public Figures' Proposals & Real-Time Voter Vision Alignment</p>
    </header>
    <div class="meta-bar">
        Last Automated Global Scan: <strong>{last_updated}</strong> | Tracked Ideas: <strong>{len(proposals)}</strong> | License: MIT (100% Open-Source Civic Utility)
    </div>
    <main>
        {cards_html}
    </main>
    <footer>
        Powered by Python & Gemini AI | Open-Source Democratic Accountability Framework
    </footer>

    <script>
        // Client-side Real-Time Voter Alignment Engine (Vot in Timp)
        function loadVotes() {{
            const saved = JSON.parse(localStorage.getItem('vot_in_timp_data') || '{{}}');
            for (const [propId, counts] of Object.entries(saved)) {{
                updateUI(propId, counts.yes || 0, counts.no || 0);
            }}
        }}

        function castVote(propId, choice) {{
            const saved = JSON.parse(localStorage.getItem('vot_in_timp_data') || '{{}}');
            if (!saved[propId]) {{
                saved[propId] = {{ yes: 0, no: 0 }};
            }}
            if (choice === 'fulfills') {{
                saved[propId].yes += 1;
            }} else {{
                saved[propId].no += 1;
            }}
            localStorage.setItem('vot_in_timp_data', JSON.stringify(saved));
            updateUI(propId, saved[propId].yes, saved[propId].no);
        }}

        function updateUI(propId, yesCount, noCount) {{
            const yesEl = document.getElementById(propId + '-yes');
            const noEl = document.getElementById(propId + '-no');
            const barEl = document.getElementById(propId + '-bar');
            const statsEl = document.getElementById(propId + '-stats');
            if (!yesEl || !noEl) return;

            yesEl.textContent = yesCount;
            noEl.textContent = noCount;

            const total = yesCount + noCount;
            const yesPct = total === 0 ? 50 : Math.round((yesCount / total) * 100);
            const noPct = 100 - yesPct;

            barEl.style.width = yesPct + '%';
            statsEl.textContent = `Real-Time Alignment Score: ${{yesPct}}% Fulfills Vision / ${{noPct}}% Fails Vision (${{total}} total votes cast)`;
        }}

        document.addEventListener('DOMContentLoaded', loadVotes);
    </script>
</body>
</html>
"""
    with open(HTML_OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_template)


def main():
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable is missing.")

    initialize_directories()
    proposals = load_existing_proposals()
    existing_urls = {item["source_url"] for item in proposals}

    print("Scanning global political news feeds for public figure proposals...")
    candidate_articles = fetch_global_news(existing_urls)
    print(f"Found {len(candidate_articles)} new articles to evaluate.")

    client = genai.Client(api_key=GEMINI_API_KEY)
    new_count = 0

    for article in candidate_articles:
        if new_count >= MAX_NEW_PROPOSALS_PER_RUN:
            break

        print(f"Evaluating: {article['title']}")
        analysis = analyze_public_figure_idea(client, article)

        if analysis.get("is_valid_proposal"):
            proposals.append({
                "date": datetime.date.today().isoformat(),
                "original_title": article["title"],
                "source_url": article["link"],
                "analysis": analysis
            })
            new_count += 1
            print(f" -> Indexed proposal by {analysis.get('public_figure')} [{analysis.get('implementation_status')}].")

    save_proposals(proposals)
    render_static_website(proposals)
    print(f"Pipeline complete. Indexed {new_count} new proposals and updated {HTML_OUTPUT_FILE}.")


if __name__ == "__main__":
    main()
