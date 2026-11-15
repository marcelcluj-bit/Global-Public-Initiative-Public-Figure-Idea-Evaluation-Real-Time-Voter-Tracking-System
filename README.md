# Global-Public-Initiative-Public-Figure-Idea-Evaluation-Real-Time-Voter-Tracking-System
Here is the complete, professional open-source project framework written entirely in English, tailored for any public figure or politician worldwide. It evaluates their public proposals (regardless of whether they are implemented or not) and incorporates a real-time voting mechanism.for voters to judge whether future initiators fulfill their vision
This script monitors international news feeds for policy proposals or public statements made by any public figure/politician worldwide, evaluates whether the idea is Proposed, In Progress, Implemented, or Abandoned/Contradicted, generates the full 8-point project management blueprint via gemini-2.5-flash, and builds the interactive docs/index.html portal equipped with the Vot în Timp real-time voter alignment tracker
# Global Politician Idea Tracker & Vot în Timp Accountability Portal

Repository Structure

global-politician-tracker/
├── .github/
│   └── workflows/
│       └── daily_global_scan.yml   # Automated daily GitHub Action
├── data/
│   └── proposals.json              # Database of public figures, ideas & implementation status
├── docs/
│   └── index.html                  # Interactive public web portal with Vot în Timp module
├── main.py                         # Core Python script (Scraper + Gemini AI + Site Builder)
├── requirements.txt                # Python dependencies
├── LICENSE                         # MIT License
└── README.md                       # English documentation & setup guide




An open-source AI pipeline powered by Python and Google Gemini that tracks policy ideas, campaign promises, and public initiatives proposed by politicians and public figures worldwide.

## Key Capabilities
1. **Global Proposal Ingestion & Execution Audit**: Automatically detects policy ideas from global news feeds and classifies their real-world status (**Proposed**, **In Progress**, **Implemented**, or **Abandoned / Contradicted**), regardless of whether the blueprint is publicly shared or kept closed.
2. **8-Point Project Management Blueprint**: Generates a complete Stakeholder Analysis, Problem Tree, Objective Tree, SWOT Analysis, Ishikawa (Fishbone) Diagram, Logical Framework (LogFrame), Gantt Activity Schedule, and Estimated Budget for every tracked idea.
3. **Vot în Timp (Real-Time Voter Vision Alignment)**: Interactive voter evaluation module allowing citizens to continuously vote on whether a public figure or future project initiator is fulfilling their stated vision.

## Quick GitHub Deployment
1. Create a new repository on GitHub and upload these files.
2. Navigate to **Settings > Secrets and variables > Actions** and add your `GEMINI_API_KEY`.
3. Navigate to **Settings > Pages**, set **Source** to `Deploy from a branch`, choose `main` and `/docs`, and click **Save**.
4. Go to **Actions > Daily Global Politician Idea Scan & Site Builder** and click **Run workflow**.

5. LICENSE (MIT License)
Plaintext
MIT License

Copyright (c) 2026 Global Politician Idea Tracker Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
