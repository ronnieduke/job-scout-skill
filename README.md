# Job Scout

End-to-end job search automation: scan career pages, filter by your criteria, track your pipeline, prep for interviews, practice with mock sessions, and log every activity for unemployment compliance. Works with Claude Code.

## Recommended Setup: MARVIN + Job Scout

Job Scout works best inside **MARVIN** (Manages Appointments, Reads Various Important Notifications), an AI Chief of Staff that maintains context across sessions. Without MARVIN, every conversation starts from scratch. With it, Claude remembers your search history, tracks your pipeline over days and weeks, and can help with other areas of your life (goals, schedule, content).

### Why MARVIN matters for job seekers

- **Session continuity**: Claude remembers yesterday's scan results, which roles you liked, what you applied to
- **Pipeline tracking**: Your job pipeline persists across conversations without you re-explaining where things stand
- **Beyond job search**: MARVIN handles personal goals, weekly planning, meeting prep, and more. Your job search lives alongside everything else.

### Step 1: Clone MARVIN

```bash
git clone https://github.com/SterlingChin/marvin-template.git my-workspace
cd my-workspace
```

### Step 2: Install Job Scout

Copy the `job-scout` folder into `skills/`:

```
my-workspace/
  skills/
    job-scout/    <-- put it here
```

### Step 3: Choose Your Interface

You'll interact with Job Scout (and MARVIN) through Claude Code. There are three ways to run it:

**Cursor with Claude Code Extension (Recommended)**
Cursor is a code editor with a built-in file tree and chat panel. Install the Claude Code extension from the marketplace, open your workspace folder, and you're set. Job Scout generates reports, pipeline trackers, and resume drafts as files in your project. With Cursor, you see them appear in the sidebar and can click to open them. This visibility makes the whole workflow feel tangible. Best option for Job Scout specifically.

**Claude Code Desktop**
A standalone chat app. Cleaner interface, no file tree or editor pane. You'd keep a Finder/Explorer window open alongside it to view generated files, or ask Claude to show file contents in the chat. The upside: you can switch between Claude Code mode (for running skills) and regular chat mode (for brainstorming, research, general questions). If you want Claude as a broader thinking partner beyond job search, Desktop gives you that flexibility.

**Terminal (Claude Code CLI)**
The original interface. Fast, flexible, no GUI overhead. If you're comfortable in a terminal, this is the most efficient option. Install with `npm install -g @anthropic-ai/claude-code`, then run `claude` in your workspace directory.

All three give you the same Job Scout capabilities. Pick whichever fits how you work.

### Step 4: Run Onboarding

Open your workspace in your chosen interface and type:

```
/job-onboard
```

This starts an interactive conversation where Claude will:

1. **Ask about you** - your name, experience, what you do
2. **Learn what you're looking for** - target roles, salary range, remote preference
3. **Help you pick companies to watch** - Claude finds the right career page URLs for you
4. **Set up everything automatically** - config files, pipeline tracker, resume template
5. **Run a test scan** - make sure it all works
6. **Install any missing software** - Python packages, optional tools

You don't need to know anything about APIs, board tokens, or config files. Claude walks you through everything.

## Standalone Setup (Without MARVIN)

Job Scout works in any Claude Code project. You lose cross-session memory, but scanning and filtering work the same.

1. Create a project folder and open it in Claude Code
2. Create a `skills/` directory: `mkdir -p skills`
3. Copy the `job-scout` folder into `skills/`
4. Run `/job-onboard`

## What You Need

1. **Claude Code** installed via any of the three interfaces above ([install guide](https://docs.anthropic.com/en/docs/claude-code/overview))
2. **Python 3.8+** (check with `python3 --version` in your terminal)
3. That's it. Job Scout handles everything else during setup.

## Commands

| Command | What It Does |
|---------|-------------|
| `/job-onboard` | Interactive setup wizard. Run once to configure, re-run to update. |
| `/job-scout` | Scan target companies, filter results, update pipeline. |
| `/interview-prep` | Generate an interview kit: company research, comp data, talking points, Q&A. |
| `/mock-interview` | Practice interview with real-time coaching using your prep kit. |

## Daily Use

Once set up, run your daily scan:

```
/job-scout
```

Claude will:
- Scan all your target companies for new job postings
- Filter out roles that don't match your criteria
- Show you what's new with salary info and screening signals
- Suggest checking your network for referrals before you apply
- Offer to add promising roles to your pipeline
- Help tailor your resume for specific roles
- Log the scan and any applications to your activity log

## Automated Scanning

You can schedule Job Scout to run automatically so new matches are waiting for you each morning. The scanner runs as a standalone Python script, no Claude Code session required.

### macOS (launchd)

Create a plist file at `~/Library/LaunchAgents/com.jobscout.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.jobscout</string>

    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/your/workspace/skills/job-scout/scripts/job-scout.py</string>
    </array>

    <key>WorkingDirectory</key>
    <string>/path/to/your/workspace</string>

    <key>StartCalendarInterval</key>
    <array>
        <!-- 8am -->
        <dict>
            <key>Hour</key>
            <integer>8</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
        <!-- Noon -->
        <dict>
            <key>Hour</key>
            <integer>12</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
        <!-- 3pm -->
        <dict>
            <key>Hour</key>
            <integer>15</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
    </array>

    <key>StandardOutPath</key>
    <string>/path/to/your/workspace/state/job-scout-last-run.log</string>

    <key>StandardErrorPath</key>
    <string>/path/to/your/workspace/state/job-scout-last-run.log</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin</string>
    </dict>
</dict>
</plist>
```

Replace `/path/to/your/workspace` with your actual workspace path. Then load it:

```bash
launchctl load ~/Library/LaunchAgents/com.jobscout.plist
```

To stop it:
```bash
launchctl unload ~/Library/LaunchAgents/com.jobscout.plist
```

Adjust the `StartCalendarInterval` entries to change the schedule. The example runs at 8am, noon, and 3pm local time.

### Linux (cron)

Open your crontab:

```bash
crontab -e
```

Add a line for each scan time. This example runs at 8am, noon, and 3pm:

```
0 8,12,15 * * * cd /path/to/your/workspace && /usr/bin/python3 skills/job-scout/scripts/job-scout.py >> state/job-scout-last-run.log 2>&1
```

### Windows (Task Scheduler)

1. Open Task Scheduler and create a new task
2. Set the trigger to your preferred schedule (e.g., daily at 8am, noon, 3pm)
3. Set the action to run a program:
   - **Program:** `python3`
   - **Arguments:** `skills/job-scout/scripts/job-scout.py`
   - **Start in:** `C:\path\to\your\workspace`
4. Optionally redirect output by wrapping in a batch script that appends to `state\job-scout-last-run.log`

### Checking Results

After an automated run, the report is at `research/output/YYYY-MM-DD-job-scout-results.md` (using the date of the run). The last run log is at `state/job-scout-last-run.log`. Next time you open Claude Code, run `/job-scout` and it will pick up where the automated scan left off, showing you new matches and offering next steps.

## Interview Prep

When you land an interview, generate a prep kit:

```
/interview-prep Acme
```

Claude will research the company, pull comp data from multiple sources, write stage-specific talking points, build a comp negotiation strategy with scripts, and generate likely questions with suggested answers tailored to your background. The kit is saved locally and reused across stages.

## Mock Interviews

Practice before the real thing:

```
/mock-interview Acme
```

Claude plays the interviewer using questions sourced from your prep kit (reworded so you're practicing articulation, not recall). After each answer, a coaching voice gives direct, specific feedback: what landed, what to tighten, and angles from the kit you might be missing. Sessions can be quick (5 questions), full (8-12), targeted ("just leadership questions"), or focused on comp negotiation with adjustable difficulty. Transcripts and summaries are saved so you can track improvement across sessions.

## Activity Logging

Every job-seeking activity is logged to `state/activity-log.md`, a chronological record designed for unemployment compliance. Many states require weekly proof of active job search to receive benefits. Job Scout handles this automatically.

**Auto-logged by commands:** job search scans, applications, interview prep kit generation, mock interview sessions.

**Logged from conversation:** When you mention sending a follow-up email, taking an interview, making a networking call, or doing company research, Claude logs it without you having to ask. You just say "I had my Acme screener today" and it gets recorded.

The log is a simple markdown table: date, activity type, company, role, and a brief detail. Easy to review, copy into a state unemployment portal, or hand to anyone who asks for proof of job search activity.

## What It Scans

Job Scout checks 6 major hiring platforms that most companies use:

| Platform | Companies Using It |
|----------|-------------------|
| Greenhouse | Airbnb, Anthropic, Cloudflare, Datadog, Figma, Stripe, etc. |
| Lever | Clari, Outreach, Netflix, etc. |
| Ashby | Notion, Cohere, Ramp, etc. |
| Workable | 30,000+ mid-market companies |
| Recruitee | European and global companies |
| Workday | Adobe, Salesforce, Disney, PayPal, Intel, etc. |

## How It Works

```
/job-onboard
  Set up your profile, target roles, companies, screening criteria
        |
        v
/job-scout
  Scan career pages → filter by title → screen on 6 signals → show new matches
  You pick which to pursue → check network for referrals → apply → log activity
        |
        v
/interview-prep
  Research company → pull comp data → generate talking points and Q&A
  Builds a full interview kit tailored to the role and stage
        |
        v
/mock-interview
  Practice against your kit → get coaching feedback → save transcript
  Track improvement across sessions → log activity
        |
        v
state/activity-log.md
  Every step is logged: scans, applications, prep, practice, interviews,
  emails, calls. Ready for unemployment filing or personal reference.
```

## Files It Creates

After setup, Job Scout creates these files in your project:

```
skills/job-scout/config/
  watchlist.json                          Your target companies and filter settings
  profile.json                            Your search profile

state/
  jobs.md                                 Your job pipeline tracker
  job-scout-seen.json                     Tracks which jobs you've already seen
  activity-log.md                         Chronological activity log (for unemployment filings)

content/
  jobs/
    company-role-title.md                 Archived job descriptions
  interview-kit-company.md                Interview prep kits
  mock-interview-company-YYYY-MM-DD.md    Mock interview transcripts and coaching summaries

research/output/
  YYYY-MM-DD-job-scout-results.md         Daily scan reports
  YYYY-MM-DD-company-interview-prep.md    Company research
  YYYY-MM-DD-company-role-salary.md       Comp research
```

Job descriptions are archived automatically when you add a role to your pipeline. This matters because postings can be taken down at any time, sometimes before you even get a screening call. The archived copy gives you the full original JD for interview prep, resume tailoring, and reference.

Everything builds on itself: scan results feed the pipeline, the pipeline feeds interview prep, prep kits feed mock interviews, and every step is logged to the activity record.

## Optional Extras

These companion tools make the workflow even better. Claude will suggest them during setup if they're not installed.

| Tool | What It Does | Cost |
|------|-------------|------|
| Resume Tailoring Skill | Auto-generates role-specific resumes from your base template | Free |
| LinkedIn Jobs Skill | Searches LinkedIn for jobs not on the 6 platforms above | ~$1.50/1k results |
| Playwright (Python) | Enables scanning Workday companies that block the default method | Free |

### LinkedIn Search Setup

The LinkedIn Jobs skill requires a BrightData API key. To set it up:

1. Sign up at [brightdata.com](https://brightdata.com) and create a Web Scraper API token
2. Copy `.env.example` to `.env` in your project root (or add to your existing `.env`):
   ```bash
   cp skills/job-scout/.env.example .env
   ```
3. Add your key:
   ```
   BRIGHTDATA_API_KEY=your-api-key-here
   ```

The `.env` file is gitignored by default. Core scanning works without it.

## Troubleshooting

**"No watchlist configured"** - Run `/job-onboard` first to set up your search.

**"requests module not found"** - Claude will install it automatically. If not, run: `pip install requests`

**Workday companies showing errors** - Most Workday companies work out of the box. If one doesn't, Claude will suggest installing Playwright.

**No new matches** - That's normal if you ran a scan recently. Job Scout remembers what it's shown you. Use `--reset` to start fresh.

## Privacy

- Job Scout only reads public job postings from company career pages
- Your search profile and config stay local on your machine
- Nothing is sent to external services (unless you opt into LinkedIn search via BrightData)
- No accounts or API keys required for the core scanning functionality
