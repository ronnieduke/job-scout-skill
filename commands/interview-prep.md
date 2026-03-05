# /interview-prep - Generate Interview Prep Kit

Build a complete interview prep kit: company research, comp data, talking points, and tailored Q&A for any stage.

## Instructions

### Overview

This is a multi-step research and content generation process. The output is a comprehensive interview kit saved to `content/interview-kit-{company-slug}.md`. If a previous interview kit exists in `content/`, use it as a quality benchmark. Match that level of specificity and usefulness.

**Tone:** Conversational, confident, direct. The kit should sound like a real person prepping another real person for a conversation, not a corporate interview guide. Answers should feel natural to say out loud.

---

### Step 1: Gather Context

Before asking a single question, check what you already know.

**Read these files (silently, don't dump raw data at the user):**

1. `state/jobs.md` — Check if the company/role is already in the pipeline. Pull: company, role, stage, contacts, referral, dates, notes.
2. `skills/job-scout/config/profile.json` — Candidate background, target roles, comp floor/target, dealbreakers, preferences.
3. `research/output/` — Any existing research on this company (glob for `*{company}*`).
4. `content/` — Any existing interview kit for this company (glob for `interview-kit-{company}*`).
5. `content/stories.md` — Existing story inventory (if it exists).
6. `content/debrief-{company-slug}-*.md` — Previous interview debriefs for this company. If debriefs exist, use the real questions asked and interviewer signals to inform kit generation or updates.

**If the role is already in `state/jobs.md`:**

Pre-fill everything you can and confirm with the user:

> "I see you've got [Role] at [Company] in your pipeline. Here's what I have:
> - Stage: [stage]
> - Contact: [name]
> - Referral: [name]
> - Date: [date]
>
> Anything to update before I start building the kit?"

**If the role is NOT in the pipeline, ask for:**

- Company name (required)
- Role title (required)
- Interview stage: recruiter screen, hiring manager, panel, or final
- Interview date/time (if scheduled)
- Key contacts (recruiter, hiring manager, referral)
- Any specific concerns, angles, or topics they want covered

Don't ask for everything in a wall of questions. Group naturally: "What company and role?" Then: "What stage are you at and when is it?" Then: "Anyone specific I should know about — recruiter, referral, hiring manager?"

**If an existing interview kit exists for this company:**

> "You already have an interview kit for [Company]. Want me to update it for a new stage, refresh the research, or start from scratch?"

If updating for a new stage, preserve the research sections and regenerate the stage-specific content (questions, talking points, questions to ask).

If a debrief exists for a previous round (`content/debrief-{company-slug}-*.md`), incorporate what was learned:
- Add the real questions that were asked to the "Likely Questions" section
- Adjust talking points based on what landed well and what didn't
- Update concerns based on interviewer signals (what they pushed back on, what they seemed satisfied with)
- Note any new intel about the team, role, or process that came out in the interview

---

### Step 2: Get the Job Description

Check for an existing JD: `content/jobs/{company-slug}-{role-slug}.md`

**If found:** Read it. Confirm it's still the right version. Move on.

**If not found:**

1. Check if the company is in `skills/job-scout/config/watchlist.json` and has an ATS entry.
2. If yes, try to find and fetch the JD from their careers page via web search.
3. If no, ask the user: "Can you share the JD? Either paste it or give me a URL."

**Save the JD** to `content/jobs/{company-slug}-{role-slug}.md` with a header:

```markdown
# {Company} — {Role Title}

**Source:** {URL or "provided by user"}
**Saved:** {YYYY-MM-DD}

---

{JD content}
```

---

### Step 2b: Story Collection

Check if `content/stories.md` exists.

**If it doesn't exist:** This is the first prep run. Ask the user for 5-8 go-to professional examples:

> "Before I build the kit, I want to know what stories you have in your back pocket. Give me 5-8 examples from your career — projects, wins, failures you learned from, leadership moments. For each one: what happened, what skills it shows, and what the result was. These become your story inventory — I'll map them to likely questions and use them across prep and mock sessions."

Create `content/stories.md` with the inventory table format (see SKILL.md "Story Inventory" section).

**If it already exists:** Read it silently. No need to ask again. You'll map these stories to questions in Step 5.

**If a debrief exists for this company:** Note which questions were actually asked in a previous round. When generating the kit, prioritize those topics and map stories to them.

---

### Step 2c: Hard-Won Insights

Before generating the kit, surface the user's counterintuitive insights from real experience. These make answers memorable and hard to replicate.

**If this is the first kit (no previous kits exist):** Ask 3-5 reflection questions. Don't ask all at once — weave them naturally into the conversation:

- What did you believe before starting [most relevant project/role] that turned out to be wrong?
- What would surprise someone who hasn't done this kind of work?
- What do most people in your field get wrong about [topic relevant to the target role]?
- What counterintuitive lesson did a specific failure teach you?
- What's something you'd do differently if you could redo [relevant project], and why?

Pick the 2-3 most relevant questions based on the role. Don't ask all five.

**If previous kits exist:** Check if hard-won insights were already captured. If so, reuse them. If the role is substantially different, ask 1-2 new reflection questions targeted at the new role's requirements.

**Use the answers to:**
- Weave the strongest insights into the "Tell Me About Yourself" narrative as differentiators
- Flag them in the kit with a note: *"Differentiator — use this to stand out"*
- Reference them in talking points where they naturally fit

---

### Step 3: Company Research

Use web search to build a company profile. Be specific and current. Generic "Company X is a leader in..." filler is useless.

**Research these areas:**

1. **What the company does** — Plain language. Business model, who their customers are, what they sell, how they make money.
2. **Size and financials** — Revenue (or estimated), employee count, public/private, funding stage if private, growth trajectory.
3. **Products/platform** — Key product lines, recent launches, how they're positioned against competitors.
4. **Recent news (last 6 months)** — Acquisitions, partnerships, leadership changes, earnings, layoffs, product launches. Prioritize news that's relevant to the role.
5. **Leadership** — CEO, relevant C-suite (CMO if it's a marketing role, CTO if it's tech), and the hiring manager's org if you can find it on LinkedIn.
6. **Culture signals** — Glassdoor overall rating, notable employee sentiment themes, stated values (but note the gap between stated and real if obvious).
7. **Why this role exists** — Infer the business need. Is this a new team? Replacement? Growth hire? What strategic initiative does this role serve?

**Save research to:** `research/output/YYYY-MM-DD-{company-slug}-interview-prep.md`

**If research already exists** (from a previous run or another source):

> "I found existing research on [Company] from [date]. Want me to use it as-is, or refresh it with current data?"

If refreshing, overwrite with new date in the filename.

---

### Step 4: Compensation Research

Search across multiple sources. Don't rely on a single data point.

**Sources to check:**

1. **Glassdoor** — Search for the company + title (and similar titles)
2. **Levels.fyi** — Company + level comp data (especially useful for tech companies)
3. **Blind / TeamBlind** — Comp discussion threads for the company
4. **Peer comparables** — Same title/level at 2-3 similar-size companies in the same space

**Synthesize into:**

- Estimated base salary range
- Bonus target (% and estimated dollar amount)
- Equity/RSU value (if applicable — annual vesting estimate)
- Total comp range
- Data sources with confidence level (strong data vs. limited data points)

**Cross-reference with profile.json:**

- Pull `comp_floor` and `comp_target` from the candidate profile
- Flag whether this role: meets floor, hits target, exceeds target, or falls short
- If it falls short, note it clearly so the user can decide whether to proceed

**Save to:** `research/output/YYYY-MM-DD-{company-slug}-{role-slug}-salary.md`

---

### Step 5: Generate the Interview Kit

Read the template at `skills/job-scout/templates/interview-kit-template.md` for section structure and tone guidance.

Generate the kit with these sections:

#### 5.1 Header
Company, role, stage, date/time, contacts, referral. Quick reference block.

#### 5.2 Quick Reference
Condense the company research into ~15 lines. The user should be able to glance at this 5 minutes before the call and know the essentials.

#### 5.3 Strategic Context
What's happening at the company that makes this role matter right now? Leadership decisions, market moves, org changes. Connect the dots between company strategy and this specific hire.

#### 5.4 "Tell Me About Yourself" (90 seconds)
Write a narrative that connects the candidate's background (from profile.json and resume) to THIS specific role. Not a generic career summary. A story that ends with "...and that's why this role is interesting to me."

Structure: career arc (2-3 sentences) → most relevant recent work (2-3 sentences) → why this role (1-2 sentences).

Weave in hard-won insights from Step 2c where they naturally fit. A counterintuitive insight early in the narrative makes the whole answer more memorable. Flag any used with *"Differentiator — use this to stand out"* in italics.

#### 5.5 Why This Company
2-3 authentic, specific reasons based on the research. Not "I love your mission." Real things: specific strategic decisions, product direction, market position, cultural signals. Things that show genuine understanding.

#### 5.6 Why This Role
Tied to JD specifics and the candidate's actual strengths. What in the JD maps to what they've done? Be specific about the connection.

#### 5.7 Likely Concerns + Counter-Evidence

Identify 3-5 things the interviewer might worry about based on the resume, JD gaps, career arc, or role mismatch. For each concern:

- **The concern:** What they might be thinking (e.g., "No enterprise SaaS experience," "Job-hopping," "Overqualified for this level")
- **How it surfaces:** The question or probe they'll use to test it (e.g., "Tell me about your experience with enterprise sales cycles")
- **What they're looking for:** The signal that would address or confirm their worry
- **Counter with evidence:** A specific example, reframe, or data point that addresses the concern directly

Sources for identifying concerns:
- Gaps between the JD requirements and the candidate's resume/profile
- Career arc patterns (short tenures, industry switches, level changes)
- Role mismatch signals (overqualified, underqualified, lateral move)
- Common biases for the role type (agency background applying to in-house, B2C applying to B2B, etc.)

If a debrief from a previous round exists, use interviewer signals to validate or adjust concerns. If they pushed back on something specific, it's a confirmed concern — address it head-on.

Map counter-evidence to stories from the story inventory where possible.

#### 5.8 Comp Discussion
Build a comp strategy section with scripts for different scenarios:
- Default strategy: get them to share the range first
- Deflection scripts (2-3 levels of pushback)
- Response if range is strong
- Response if range is low
- Response if asked about current/previous comp
- Include any relevant state laws about comp disclosure

Base this on the salary research from Step 4.

#### 5.9 Likely Questions + Talking Points
Stage-appropriate questions and suggested answers.

**Recruiter screen questions:**
- Why are you looking?
- What do you know about [Company]?
- Walk me through your experience with [core skill from JD]
- Comp expectations
- Timeline / other interviews
- Remote/location
- Why you left your last role (if applicable)

**Hiring manager questions:**
- Technical depth on JD requirements
- Leadership style / team management
- Specific project examples
- How you'd approach the role
- Biggest challenge in a similar role

**Panel/final questions:**
- Cross-functional collaboration scenarios
- Strategic thinking / prioritization
- Culture and values alignment
- Conflict resolution examples

Tailor to the specific stage. Don't generate all stages unless the user asks.

Answers should sound natural. Write them as things a person would actually say, not corporate interview speak.

**Story mapping:** For each question, reference the most relevant story from `content/stories.md` if one exists. Note which story to use in italics after the talking point. If no story maps well, note the gap so mock sessions can focus on it.

#### 5.10 Questions to Ask
4-6 questions tailored to the stage and company. Each with a brief note on WHY to ask it (what signal you're getting).

**Recruiter stage:** Team structure, remote policy, interview process, role scope, timeline.
**Hiring manager:** Strategic priorities, what success looks like, team dynamics, current challenges.
**Panel/final:** Cross-team collaboration, growth plans, company direction.

#### 5.11 Green and Red Flags
Based on the user's dealbreakers and preferences from profile.json.

**Green flags:** Signals that this role is a good fit.
**Red flags:** Signals that should give pause. Include specific things to listen for.

#### 5.12 Logistics Checklist
Practical reminders:
- Date/time confirmation
- Prep items to review before the call
- Platform (Zoom, Teams, phone)
- Scheduling conflicts to watch for
- Who to mention (referral, mutual connections)

**Save the kit to:** `content/interview-kit-{company-slug}.md`

---

### Step 6: Present and Iterate

Don't dump the entire kit. Highlight the most important sections:

1. Show the "Tell Me About Yourself" narrative and ask if it feels right
2. Show the comp strategy and research summary
3. Show 2-3 of the most likely questions with talking points
4. Show the questions to ask

Then offer:

> "Full kit is saved to `content/interview-kit-{company-slug}.md`. Want me to adjust any of the talking points, refine the comp strategy, or add anything specific?"

**Also offer:**
- "Want to practice? Run `/mock-interview` to do a mock session using this kit."
- "Want me to generate a version for the next stage when you get there?"
- "Should I update your pipeline tracker with the interview details?"

If the user wants the pipeline updated, modify `state/jobs.md` with the current stage, date, and any new contacts.

---

### Step 7: Log Activity

After the kit is saved, append an entry to `state/activity-log.md`.

**If the file doesn't exist, create it with the standard header** (see SKILL.md "Activity Logging" section for format).

**Append a row:**

```
| {YYYY-MM-DD} | Interview prep | {Company} | {Role} | Generated interview kit for {stage} stage. Saved to content/interview-kit-{company-slug}.md |
```

If updating an existing kit rather than creating new:

```
| {YYYY-MM-DD} | Interview prep | {Company} | {Role} | Updated interview kit for {new stage} stage |
```

---

### Important Notes

- **Quality benchmark is any existing kit.** If a previous interview kit exists in `content/`, read it for reference on tone, depth, and structure.
- **Specificity over comprehensiveness.** A few well-researched, specific talking points beat a wall of generic advice.
- **Answers should be speakable.** Read them out loud mentally. If they sound like a press release, rewrite them.
- **Don't fabricate research.** If you can't find comp data or news, say so. "Limited data available" is better than made-up numbers.
- **Respect the user's time.** Don't ask questions you can answer from existing files. Pre-fill aggressively.
- **Each run should build on the last.** If research exists, reuse it. If a kit exists, offer to update rather than rebuild.
