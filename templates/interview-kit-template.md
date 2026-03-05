# Interview Kit Template

This is a style guide for generating interview kits, not a fill-in-the-blank form. Use this structure for every kit, but adapt the depth and emphasis based on the role, stage, and company.

**Reference:** If a previous interview kit exists in `content/`, use it as the quality benchmark. Match that level of specificity and practical usefulness.

---

## Tone and Style

- **Conversational and confident.** The person reading this is about to have a conversation, not deliver a presentation. Every answer should feel natural to say out loud.
- **Specific over generic.** "I admire your mission" is useless. "Your recent acquisition of [Company X] signals you're serious about AI search, and I've been building exactly that kind of integration" is useful.
- **Direct.** No filler. No "Here's the thing:" or "It's worth noting that..." Just say it.
- **Honest about gaps.** If comp data is thin, say so. If a red flag exists, name it. The kit should help the user make decisions, not just feel good.
- **Answers in blockquotes.** Suggested verbal responses go in `> blockquote` format so they stand out visually.
- **Strategy notes in italics.** Tactical advice about WHY to say something goes in `*italic*` after the answer.
- **Hard-won insights stand out.** When a talking point contains a counterintuitive insight from the candidate's real experience, flag it with *"Differentiator — use this to stand out"* in italics. These make answers memorable and hard to replicate. Weave them naturally into narratives, especially "Tell Me About Yourself."

---

## Section Structure

### Header

```markdown
# Interview Kit: {Company} — {Role Title}

**Stage:** {Recruiter Screen | Hiring Manager | Panel | Final}
**When:** {Day M/D, time PT}
**Referral:** {Name and context, or "None"}
**Hiring Manager:** {Name and title if known}
**Applied:** {YYYY-MM-DD}
```

Keep this tight. 5 lines max. The user glances at this to remember logistics.

---

### Quick Reference: What {Company} Does

~15 lines. Plain language. Answer: what do they sell, who buys it, how big are they, what's their deal right now?

Include:
- Ticker / revenue / growth rate (if public)
- Customer base size and notable names
- Employee count / HQ location
- CEO and relevant C-suite
- One-sentence competitive positioning

This section is for the "What do you know about us?" question. The user should be able to scan this and sound informed.

---

### Strategic Context

What's happening at the company that makes this role relevant? This is the "connect the dots" section:
- Recent strategic decisions by leadership
- Market moves, acquisitions, product launches
- Why this specific role was created or opened
- What the hiring manager's org is trying to accomplish

2-4 short paragraphs. This feeds into "Why This Company" and "Why This Role" answers.

---

### "Tell Me About Yourself" (90 seconds)

A scripted narrative in blockquote format. Structure:

1. **Career arc** (2-3 sentences) — The through-line, not a chronological resume read.
2. **Most relevant recent work** (2-3 sentences) — Specific accomplishments that map to this role's requirements.
3. **Why this role** (1-2 sentences) — Connect the dots between what you've done and what this role needs.

This should feel like a natural story, not a list of bullet points read aloud. End with forward momentum: why this opportunity specifically.

If the candidate surfaced hard-won insights during prep (counterintuitive lessons from real experience), weave the strongest one into this narrative. A surprising insight early on makes the entire answer more memorable.

---

### Why {Company}

2-3 reasons. Each one should be:
- Specific to THIS company (not interchangeable with any competitor)
- Based on actual research (news, strategy, product)
- Authentic (something the candidate genuinely cares about)

Format as bold label + paragraph. Example:

> **The platform approach resonates.** [Specific thing about how the company builds/thinks that connects to the candidate's philosophy]

---

### Why This Role

Tied to the JD. For each point:
- Name the JD requirement or responsibility
- Connect it to something the candidate has done
- Show why it's exciting, not just qualified

Avoid: "I have 10 years of experience in X." Prefer: "The JD calls out [specific thing] — I did exactly this at [Company] when I [specific example]."

---

### Likely Concerns + Counter-Evidence

3-5 things the interviewer might worry about. For each:

```markdown
#### {Concern}

**Why they might worry:** {1-2 sentences explaining the gap or pattern they'll notice}

**How it surfaces:** {The question or probe they'll use}

**What they're looking for:** {The signal that would satisfy or confirm the concern}

**Counter:**
> {Specific response with evidence — a reframe, an adjacent example, or data that addresses it directly}

*{Tactical note: which story to use, what tone to strike, what to avoid}*
```

Be honest about real gaps. The point isn't to spin — it's to prepare the candidate to handle the concern confidently rather than getting caught flat-footed. A candidate who names the gap first and then addresses it is stronger than one who pretends the gap doesn't exist.

Sources for concerns: JD vs. resume gaps, career arc patterns (short tenures, industry switches), role mismatch signals, common biases for the role type.

If previous interview debriefs exist, use interviewer pushback as confirmed concerns.

---

### Comp Discussion

Structure:
1. **Research summary** — What the data says (ranges, sources, confidence level)
2. **Candidate position** — How this maps to their floor/target
3. **Strategy** — Default approach (usually: get them to share first)
4. **Scripts** — 4-5 scenario-based responses in blockquote format:
   - If they ask your expectations
   - If they push you to go first
   - If they really insist
   - If the range is strong
   - If the range is low
   - If they ask current/previous comp

Include relevant state law notes (pay transparency, salary history bans).

---

### Likely Questions + Talking Points

Stage-appropriate. Each question gets:
- The question as an H3 heading
- A suggested answer in blockquote format
- Optional tactical note in italics

**Recruiter screen (typical 6-8 questions):**
- Why are you looking?
- What do you know about us?
- Walk me through your relevant experience
- Comp expectations
- Timeline / other interviews
- Remote/location requirements
- Why you left your last role
- Why should we consider you?

**Hiring manager (typical 5-7 questions):**
- Technical depth questions specific to JD
- Leadership/management style
- Specific project deep-dives
- How you'd approach the first 90 days
- Biggest challenge in a similar role
- Cross-functional collaboration examples

**Panel/final (typical 4-6 questions):**
- Strategic prioritization scenarios
- Conflict resolution / difficult stakeholder examples
- Culture and values
- Long-term vision for the function

Only generate questions for the relevant stage unless the user requests all stages.

---

### Questions to Ask

4-6 questions. Each one:
- In bold as the actual question to ask
- Followed by a brief note on what signal you're trying to get

Don't ask questions you can easily Google. Don't ask questions that make you look unprepared. Ask questions that show you've done homework and are evaluating fit, not just trying to impress.

Stage-appropriate:
- **Recruiter:** Team structure, remote policy, interview process, role scope
- **Hiring manager:** Strategic priorities, current challenges, what success looks like, team dynamics
- **Panel/final:** Company direction, cross-team collaboration, growth plans

---

### Green and Red Flags

Two subsections with bullet points.

**Green flags:** Signals during the conversation that this is a good fit. Based on the candidate's preferences and dealbreakers from their profile.

**Red flags:** Warning signs to watch for. Specific things they might say or avoid saying that should give pause.

Be concrete: "They hedge on remote flexibility" is more useful than "Bad culture fit."

---

### Logistics Checklist

Markdown checkbox format:

```markdown
- [ ] Confirm interview date/time
- [ ] Test video/audio setup
- [ ] Review this kit 30 min before
- [ ] Mention [referral name] early
- [ ] {Any role-specific prep items}
```

Include scheduling conflicts, platform details, and practical reminders.

---

## File Naming

- **Interview kit:** `content/interview-kit-{company-slug}.md`
- **Company research:** `research/output/YYYY-MM-DD-{company-slug}-interview-prep.md`
- **Salary research:** `research/output/YYYY-MM-DD-{company-slug}-{role-slug}-salary.md`
- **Job description:** `content/jobs/{company-slug}-{role-slug}.md`

Slugs are lowercase, hyphenated. "Acme Corp" becomes "acme-corp". "Sr. Director, Marketing Technology" becomes "sr-director-marketing-technology".
