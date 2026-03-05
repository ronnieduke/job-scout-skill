# /job-onboard - Job Search Setup Wizard

Interactive onboarding to configure your job search. Run once to set up, re-run anytime to update.

## Instructions

### Overview

This is a conversational setup. The user may have never used a terminal, Claude Code, or any job search tools before. Be warm, clear, and never assume technical knowledge. Explain things in plain language. Don't dump a form on them. Have a conversation.

**Tone:** Like a helpful career coach who also happens to be good with computers. Patient, clear, zero jargon unless you explain it first.

### 0. Pre-flight: Make Sure Everything Works

Before asking any questions, silently run these checks and fix what's broken.

**Check Python is available:**
```bash
python3 --version 2>&1
```
If Python isn't found, stop and help them install it. Link to python.org. Don't proceed without Python.

**Check and install the `requests` library:**
```bash
python3 -c "import requests; print('OK')" 2>&1
```
If missing, install it automatically:
```bash
pip3 install requests 2>&1 || pip install requests 2>&1 || python3 -m pip install requests 2>&1
```
Try multiple pip variants since beginners may have different setups.

**Create required directories:**
```bash
mkdir -p skills/job-scout/config
mkdir -p state
mkdir -p research/output
mkdir -p content/jobs
```

**Check for companion skills** (silently note what's installed):
Look for these directories:
- `skills/tailored-resume-generator/` or `.agents/skills/tailored-resume-generator/`
- `skills/linkedin-jobs/` or `.agents/skills/linkedin-jobs/`
- `skills/linkedin-personal-branding/` or `.agents/skills/linkedin-personal-branding/`

Don't mention companion skills yet. Save that for the end.

**Check for existing config:**
- `skills/job-scout/config/profile.json`
- `skills/job-scout/config/watchlist.json`

If they exist, ask: "Looks like you've set up a job search before. Want to update your settings or start fresh?"

If starting fresh, back up existing files with a `.bak` extension.

**Report the pre-flight results briefly:**
> "Everything looks good. Python's working, dependencies are installed, and we're ready to set up your search."

Or if something needed fixing:
> "Had to install a couple things, but we're all set now. Let's get started."

### 1. Learn About the User

Ask these questions conversationally. Group them in natural rounds. Don't ask everything at once.

**Round 1: Who are you?**
- What's your name?
- What do you do? (current or most recent role and industry)
- How many years of experience?
- Do you have a current resume you can share? (If so, they can give you a file path or just paste it in)

If they share a resume, read it and extract skills, tools, platforms, experience level, and career trajectory. Use this to pre-fill the config. Tell them what you found: "Based on your resume, I can see you've got deep experience with [X, Y, Z]. I'll use that to set up your search filters."

**Round 2: What are you looking for?**
- What kinds of roles are you targeting? Use plain language: "What job titles would you search for?"
- Remote, hybrid, or onsite? Any location constraints?
- What's the minimum salary you'd accept? And what's your target?
- What level? ("Are you looking for individual contributor roles, management, director-level, VP?")

**Round 3: What matters to you?**
- Any absolute dealbreakers? ("What would make you immediately skip a job posting?")
- Strong preferences? ("What do you really want but could flex on?")
- What does your ideal workday look like? ("Do you want to build things, manage people, run operations, set strategy?")

Use their answers to determine:
- Builder vs. operator preference
- Whether AI/tech relevance matters
- What keywords signal roles that are outside their scope (too technical, too junior, wrong function)

**Round 4: Screening signals**

Explain what screening does in plain language: "When I find jobs that match your title keywords, I can run them through a few extra checks to help you spot the best fits faster. Let me walk you through what's available and you tell me which ones matter to you."

Walk through each signal and ask if it's relevant. **Don't assume any signal applies.** Use their earlier answers to suggest, but let them decide:

- **Remote/Hybrid**: "Do you care whether a role is remote, hybrid, or onsite? If so, I'll flag that for each match." (Almost always relevant; include by default unless they say they don't care.)
- **Compensation**: "You mentioned your salary floor. Want me to flag roles that list salary info below that?" (Include if they gave a comp floor.)
- **Level**: "What title keywords tell you a role is the right level for you? And are there any that mean it's too junior or too senior?" Examples: someone targeting senior IC roles might want "senior", "staff", "principal" as targets and "intern", "junior", "associate" as excludes. Someone targeting management might want "manager", "director", "head of" as targets and "coordinator", "associate" as excludes. **Let them define what's right and wrong for their search.**
- **Builder vs. Operator**: "Some roles are more about building new things, others about running existing operations. Do you have a preference?" Only configure if they have a clear lean. Skip entirely for roles where this distinction doesn't apply (e.g., nursing, teaching, trades).
- **AI/Tech relevance**: "Does it matter to you whether a role involves AI or emerging technology?" Only configure if they say yes. Many roles and industries have nothing to do with AI.
- **Technical depth**: "Are there keywords that would signal a role is too deeply technical for what you're looking for?" Only configure if they're not in a deeply technical role themselves. A DevOps engineer wouldn't want to filter out "kubernetes."

For any signal they don't want, add it to `disabled_signals` in the config. For signals they want but didn't provide keywords, help them brainstorm relevant ones based on their role and industry.

**Round 5: Target companies**

Explain what this is: "I can watch specific companies' career pages and alert you when they post something matching your criteria. Think of it like a job alert, but smarter."

- "Any companies you'd love to work at? Or industries you're interested in?"
- If they name companies, YOU look up the career page and ATS platform for them. Don't ask them to find "board tokens."

**How to find a company's career page and ATS type:**
For each company the user names, search for their careers page. The URL pattern tells you the ATS:
- `boards.greenhouse.io/COMPANY` or `COMPANY.greenhouse.io` = Greenhouse (token: the slug)
- `jobs.lever.co/COMPANY` = Lever (token: the slug)
- `jobs.ashbyhq.com/COMPANY` = Ashby (token: the slug)
- `apply.workable.com/COMPANY` = Workable (token: the slug)
- `COMPANY.recruitee.com` = Recruitee (token: the subdomain)
- `COMPANY.wd#.myworkdayjobs.com/SiteName` = Workday (token: `company.wd#/SiteName`)

Use web search to find the right URL if needed. The user should never have to figure this out themselves.

If they don't have a company list, suggest: "Want me to suggest some well-known companies in [their industry] to start with? You can always add more later."

If any companies use Workday, note this internally. You'll check for Playwright later.

### 2. Build the Configuration

Based on their answers, generate both config files.

**Create `skills/job-scout/config/profile.json`:**
```json
{
  "name": "...",
  "target_roles": ["..."],
  "experience_summary": "...",
  "years_experience": 0,
  "key_skills": ["..."],
  "tools_and_platforms": ["..."],
  "comp_floor": 0,
  "comp_target": 0,
  "comp_currency": "USD",
  "location": "...",
  "remote_preference": "remote|hybrid|onsite|flexible",
  "willing_to_relocate": false,
  "dealbreakers": ["..."],
  "strong_preferences": ["..."],
  "nice_to_haves": ["..."],
  "current_resume_path": "",
  "resume_versions": [],
  "search_status": "active",
  "target_start_date": "",
  "notes": ""
}
```

**Create `skills/job-scout/config/watchlist.json`:**
Build from their answers:
- `title_include`: derived from target roles ("product manager" -> "product manager", "product management", "pm")
- `title_exclude`: roles they'd never want. If they didn't specify, use sensible defaults like "intern", "associate", "coordinator"
- `description_boost`: their key skills, tools, and technologies
- `screening` section tuned to their preferences:
  - `disabled_signals`: list of signal names the user opted out of (e.g., `["AI", "TechDepth", "Builder"]`). Valid names: `Remote`, `Comp`, `Level`, `Builder`, `AI`, `TechDepth`
  - `comp_floor`: their stated minimum (0 to disable)
  - `senior_keywords`: title keywords matching their target level (what they provided in Round 4)
  - `level_exclude_keywords`: title keywords for levels they want to skip (what they provided in Round 4)
  - `builder_keywords` / `operator_keywords`: only if they opted in during Round 4 (empty lists if not)
  - `ai_keywords`: only if they opted in during Round 4 (empty list if not)
  - `deep_eng_keywords`: only if they opted in during Round 4 (empty list if not)
  - `remote_keywords` and `hybrid_keywords`: standard defaults (unless they don't care about remote status)
- `companies`: their target list with ATS info you looked up

### 3. Set Up Pipeline Tracker

Check if `state/jobs.md` exists. If not:
- Read `skills/job-scout/templates/jobs-pipeline.md`
- Replace the placeholder header with their actual info (target roles, location)
- Write to `state/jobs.md`

If it already exists, leave it alone.

### 4. Set Up Resume Base

If they shared a resume, offer: "Want me to set up a resume template you can use as a starting point for tailoring? I'll organize your experience into a format that's easy to customize per role."

If yes, create `content/resume-base.md` using their resume formatted into the template structure from `skills/job-scout/templates/resume-base.md`.

If they didn't share a resume: "Whenever you're ready, you can share your resume and I'll set up a template for tailoring. No rush."

### 5. Show What Was Set Up

Give them a clear, non-technical summary:

> "Here's what I set up for you:"
>
> **Searching for:** [target roles]
> **Watching:** [N] companies ([list first few])
> **Salary floor:** $[X]
> **Location:** [preference]
> **Screening:** [brief description of what signals matter]
>
> **Files created:**
> - Your search config (what to look for)
> - Your profile (who you are, for resume tailoring)
> - Your pipeline tracker (to track applications)

### 6. Test Scan

Offer to run a test: "Want me to run a quick test to make sure everything works? It won't save anything, just checks that we can reach all the company career pages."

If yes:
```bash
python3 skills/job-scout/scripts/job-scout.py --verbose --dry-run
```

Report results in plain language: "Found [X] jobs across your [N] companies, and [Y] matched your search criteria. Looks like we're in business."

If there are errors, explain them plainly and fix what you can.

### 7. Companion Skills and Extras

Now mention companion skills, briefly and without pressure:

> "A couple optional extras that work well with this:"

- **If `tailored-resume-generator` is missing:** "There's a resume tailoring tool that can auto-customize your resume for specific job postings. Want me to set that up?"
- **If `linkedin-jobs` is missing:** "There's also a LinkedIn search tool that catches jobs on companies we can't scan directly. It costs about $1.50 per 1,000 results if you're interested."
- **If Workday companies were added and Playwright isn't installed:** "A few of your companies use Workday. Most should work fine, but if any have trouble, I can install a browser tool that handles them. Want me to do that now?"

If they want Playwright:
```bash
pip3 install playwright && python3 -m playwright install chromium
```

### 8. Wrap Up

> "You're all set! From now on, just type `/job-scout` whenever you want to scan for new jobs. I'll show you what's new and help you with next steps."
>
> "You can also come back to `/job-onboard` anytime to change your settings, add companies, or update your criteria."

### Important Notes

- **Never use jargon without explaining it.** "ATS", "board token", "slug", "API" - if you must use these, explain what they mean in context.
- **Do everything for them.** Don't tell them to "find the board token" - look it up yourself. Don't tell them to "run pip install" - just do it.
- **Be conversational, not form-like.** This should feel like talking to a helpful person, not filling out a form.
- **If they seem unsure**, suggest reasonable defaults and reassure them everything can be changed later.
- **Don't overwhelm.** If they just want to get started quickly, focus on the essentials (name, target roles, 3-5 companies, comp floor) and fill in the rest with sensible defaults.
- **Everything can be re-run.** Reassure them that nothing is permanent.
- **Adapt to their pace.** If they're technical and giving rapid-fire answers, match that energy. If they're uncertain and asking questions, slow down and explain more.
