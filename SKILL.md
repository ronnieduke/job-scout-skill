# Job Scout Skill

End-to-end job search automation: from finding roles to preparing for interviews to tracking everything for unemployment compliance. Works for any role or industry.

## What It Does

### Find Roles

- **ATS scanning** across Greenhouse, Lever, Ashby, Workable, Recruitee, and Workday job boards
- **Smart filtering** by title keywords, description relevance, and configurable screening signals
- **6-signal screening** to surface the best fits: Remote, Comp, Level, Builder vs. Operator, AI relevance, Technical depth
- **LinkedIn search** via BrightData API for roles that aren't on public job boards (optional, paid)
- **Deduplication** so you only see new postings each run
- **Referral prompts** before you apply, with network checking and outreach drafts

### Prepare for Interviews

- **Interview prep kits** with company research, comp data, talking points, stage-specific Q&A, and comp negotiation scripts. Generated from live research, tailored to the specific role and your background.
- **Mock interview sessions** with two voices: a realistic interviewer who asks questions based on your kit, and a coaching voice that gives direct, specific feedback after each answer. Supports recruiter screens, HM rounds, panels, and dedicated comp negotiation practice with adjustable difficulty.
- **Resume tailoring** guidance for each job description, with optional AI-powered generation via companion skill

### Track Everything

- **Pipeline tracking** with stages: Researching, Applied, Interviews, Closed
- **Activity logging** for every job-seeking action: scans, applications, interviews, prep sessions, follow-up emails, phone calls, networking. Commands log automatically. Conversational activities (calls, emails, actual interviews) are logged as they come up. The log at `state/activity-log.md` is a chronological compliance record, useful in states that require weekly proof of active job search for unemployment filings.

### Stay Organized

- **Job descriptions archived locally** so you have them even after postings come down
- **Research saved and reused** across prep sessions so you never repeat work
- **Mock interview transcripts** with coaching summaries, so you can track improvement across sessions
- **Everything builds on itself**: scan results feed the pipeline, the pipeline feeds interview prep, the prep kit feeds mock interviews, and every step is logged

## Quick Start

### 1. Run Onboarding

```
/job-onboard
```

This walks you through an interactive setup:
- Your target roles and title keywords
- Skills and experience summary (for resume tailoring)
- Comp expectations and location/remote preferences
- Companies you want to watch (with ATS board tokens)
- Screening criteria tuned to your priorities

The onboarding generates two files:
- `skills/job-scout/config/profile.json` - Your search profile and preferences
- `skills/job-scout/config/watchlist.json` - Your target companies and filter config

### 2. Run Your First Scan

```
/job-scout
```

Or run the script directly:
```bash
python3 skills/job-scout/scripts/job-scout.py
```

### 3. Review Results

Reports land in `research/output/YYYY-MM-DD-job-scout-results.md` with:
- New matches ranked by relevance
- Screening signals for each match
- Salary data when available
- Previously seen jobs still active

### 4. Track Your Pipeline

The pipeline tracker lives at `state/jobs.md`. Update it as you move through stages:
- **Interested / Researching** - Found it, looks promising
- **Applied** - Resume sent
- **Interviews** - In process
- **Closed** - Rejected, withdrew, or got an offer

## Commands

| Command | What It Does |
|---------|-------------|
| `/job-onboard` | Interactive setup wizard. Run once to configure, re-run to update. |
| `/job-scout` | Run a scan, filter results, generate report, update pipeline. |
| `/interview-prep` | Generate interview prep kit with company research, comp data, talking points, and Q&A. |
| `/mock-interview` | Practice interview with real-time coaching. Requires an interview kit. |

## CLI Options

```bash
python3 skills/job-scout/scripts/job-scout.py [options]

  --verbose, -v      Extra logging
  --reset            Clear seen-jobs state (re-scan everything)
  --company NAME     Scan a single company by name
  --dry-run          Fetch and filter but don't update state
  --no-workday       Skip Workday companies (avoids Playwright dependency)
```

## Configuration

### watchlist.json

Controls what gets scanned and how results are filtered.

```json
{
  "keywords": {
    "title_include": ["your", "target", "titles"],
    "title_exclude": ["intern", "associate"],
    "description_boost": ["relevant", "skill", "keywords"]
  },
  "screening": {
    "remote_keywords": ["remote", "distributed"],
    "hybrid_keywords": ["hybrid", "onsite"],
    "comp_floor": 150000,
    ...
  },
  "companies": [
    {
      "name": "Company Name",
      "ats": "greenhouse|lever|ashby|workable|recruitee|workday",
      "board_token": "company-slug"
    }
  ]
}
```

### profile.json

Your personal search profile, used for resume tailoring and context.

```json
{
  "name": "Your Name",
  "target_roles": ["Role A", "Role B"],
  "experience_summary": "Brief career summary",
  "key_skills": ["Skill 1", "Skill 2"],
  "comp_floor": 150000,
  "comp_target": 200000,
  "location": "City, State",
  "remote_preference": "remote|hybrid|onsite|flexible",
  "dealbreakers": ["Things you won't accept"],
  "preferences": ["Things you prefer but can flex on"]
}
```

## Finding Board Tokens

To add a company, you need their ATS board token:

- **Greenhouse:** Visit `boards.greenhouse.io/COMPANY` - the slug is the token
- **Lever:** Visit `jobs.lever.co/COMPANY` - the slug is the token
- **Ashby:** Visit `jobs.ashbyhq.com/COMPANY` - the slug is the token
- **Workable:** Visit `apply.workable.com/COMPANY` - the slug is the token
- **Recruitee:** Visit `COMPANY.recruitee.com` - the subdomain is the token
- **Workday:** Visit the company's careers page. The token format is `company.wd#/SiteName` from URLs like `company.wd5.myworkdayjobs.com/SiteName`

Not sure which ATS a company uses? Google `"COMPANY" site:greenhouse.io OR site:lever.co OR site:ashbyhq.com OR site:workable.com OR site:recruitee.com OR site:myworkdayjobs.com`.

## LinkedIn Integration (Optional)

Requires a BrightData API key. Set `BRIGHTDATA_API_KEY` in your environment. LinkedIn search queries are configured in the `linkedin` section of `watchlist.json`.

Cost: ~$1.50 per 1,000 records.

## Installation

### Python Dependencies

**Required:**
```bash
pip install requests
```

**Optional (for Workday companies):**
```bash
pip install playwright
playwright install chromium
```

Without Playwright, the scanner will first try Workday's hidden JSON API (works for many companies). If that fails, it reports an error suggesting you install Playwright. You can also use `--no-workday` to skip Workday companies entirely.

### Companion Skills (Recommended)

Job Scout works standalone, but these optional skills extend the workflow:

| Skill | What It Adds | Install |
|-------|-------------|---------|
| `tailored-resume-generator` | AI-powered resume tailoring for each JD. Job Scout finds the roles, this skill helps you apply. | `/find-skills tailored resume` |
| `linkedin-jobs` | LinkedIn job search via BrightData API. Supplements ATS scanning with LinkedIn discovery. Requires `BRIGHTDATA_API_KEY`. | `/find-skills linkedin jobs` |
| `linkedin-personal-branding` | Profile optimization and visibility analysis. Useful alongside active job searching. | `/find-skills linkedin branding` |

The `/job-onboard` wizard will check for these and suggest installing any that are missing.

## File Structure

```
skills/job-scout/
  SKILL.md                          # This file
  scripts/
    job-scout.py                    # ATS scanner and screener
  templates/
    watchlist-template.json         # Starter config (copy to config/)
    profile-template.json           # Starter profile (copy to config/)
    jobs-pipeline.md                # Pipeline tracker template
    resume-base.md                  # Resume skeleton for tailoring
    interview-kit-template.md       # Interview kit section structure and tone guide
  commands/
    job-scout.md                    # /job-scout slash command
    job-onboard.md                  # /job-onboard slash command
    interview-prep.md               # /interview-prep slash command
    mock-interview.md               # /mock-interview slash command
  config/                           # Created during onboarding (gitignored)
    watchlist.json                  # Your configured watchlist
    profile.json                    # Your search profile

state/
  activity-log.md                   # Chronological job search activity log (for unemployment filings)
```

## Activity Logging

All job-seeking activities are logged chronologically to `state/activity-log.md`. This serves as a compliance record for unemployment filings in states that require weekly proof of active job search.

### File Format

```markdown
# Job Search Activity Log

Chronological record of job-seeking activities. Useful for unemployment filings that require weekly proof of active search.

| Date | Activity | Company | Role | Details |
|------|----------|---------|------|---------|
```

### Activity Types

| Activity | When to Log | Logged By |
|----------|-------------|-----------|
| Job search scan | ATS scan completed | `/job-scout` (auto) |
| Applied | Application submitted | `/job-scout` pipeline update (auto) |
| Interview prep | Kit generated or updated | `/interview-prep` (auto) |
| Mock interview practice | Session completed | `/mock-interview` (auto) |
| Interview | Actual interview taken | Conversation (manual) |
| Follow-up email | Email sent to recruiter, HM, referral | Conversation (manual) |
| Phone call | Call with recruiter, HM, networking contact | Conversation (manual) |
| Networking | Referral outreach, informational call, intro | Conversation (manual) |
| Research | Company research for a specific opportunity | Conversation (manual) |

### Auto-Logging (Commands)

Each command logs its activity automatically after completion. The logging instructions are in the individual command files. If `state/activity-log.md` doesn't exist, create it with the header format above.

### Manual Logging (Conversation)

When the user mentions a job-seeking activity during normal conversation (sending a follow-up email, taking a phone call, having an actual interview, networking), log it to `state/activity-log.md`. Don't ask for permission every time. Just log it and mention that you did:

> "Logged that to your activity log."

Activities worth logging during conversation:
- "I just had my Acme screener" → log as Interview
- "I emailed the recruiter back" → log as Follow-up email
- "I had a call with Sarah about the Globex role" → log as Networking / Phone call
- "I sent my application to Initech" → log as Applied
- User updates pipeline stage to Interviews → log the interview

One row per activity. Keep details brief and factual.

## Resume Tailoring

After finding a match, use the `tailored-resume-generator` skill (if installed) or manually tailor using the base template at `skills/job-scout/templates/resume-base.md`.

The pipeline tracker has a Resume Versions section to track which version you sent where.
