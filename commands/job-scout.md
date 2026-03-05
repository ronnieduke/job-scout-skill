# /job-scout - Run Job Search Scan

Run the daily job scout: scan target companies, filter by your criteria, generate a report.

## Instructions

### 1. Check Configuration

Verify that the watchlist config exists. Check these paths in order:
1. `skills/job-scout/config/watchlist.json`
2. `tools/job-scout-watchlist.json`

If neither exists, tell the user:
> "No watchlist configured yet. Run `/job-onboard` first to set up your search criteria and target companies."

### 2. Run the Scanner

```bash
python3 skills/job-scout/scripts/job-scout.py --verbose
```

If the script fails due to missing `requests` library:
```bash
pip install requests && python3 skills/job-scout/scripts/job-scout.py --verbose
```

### 3. Read and Summarize Results

After the scan completes, read the generated report from `research/output/YYYY-MM-DD-job-scout-results.md` (using today's date).

Present a summary to the user:
- How many companies scanned, jobs fetched, matches found
- For each new match: company, title, location, salary (if available), and screening signal summary
- Any errors encountered

### 4. Offer Next Steps

For each promising new match, offer:
- "Want me to pull the full JD for [Company - Role]?"
- "Should I add this to your pipeline tracker?"

If the `tailored-resume-generator` skill is installed (check for `skills/tailored-resume-generator/` or `.agents/skills/tailored-resume-generator/`), also offer:
- "Want me to tailor a resume for this one?"

If it's not installed but the user asks about resume tailoring:
> "The tailored-resume-generator skill handles that. Want me to find and install it? In the meantime, there's a manual template at `skills/job-scout/templates/resume-base.md`."

If there are no new matches:
> "No new matches today. Your [X] previously seen jobs are still active. Want me to check on any of those?"

### 5. Update Pipeline (if requested)

If the user wants to add a job to their pipeline:

**First, archive the full job description.** Job postings can be taken down at any time (sometimes before the first interview), so always save a local copy the moment the user shows interest.

The scan results contain the full JD text in the `description_raw` / `description_text` fields. To archive:
```bash
python3 skills/job-scout/scripts/job-scout.py --archive-jd COMPANY_NAME "JOB_TITLE"
```

Or call the `archive_jd()` function directly if running inline. The file is saved to `content/jobs/{company-slug}-{role-slug}.md` with the complete original description, metadata, and URL.

**Never archive just a summary or snippet.** The saved file must contain the full, original job description so it can be used for interview prep, resume tailoring, and reference even after the posting is removed.

Tell the user:
> "Saved the full job description to `content/jobs/[filename]`. You'll have this even if the posting comes down."

**Then update `state/jobs.md`:**
- Add to the appropriate section (Interested/Researching, Applied, etc.)
- Include company, role, source (Job Scout), date, link to the archived JD, and any notes

### 6. Referral Check (Before Applying)

When the user has a tailored resume ready and is about to apply, **always suggest checking their network first.** A referral dramatically improves the odds of getting past the initial screen, and most companies (especially in tech) offer referral bonuses, so people are usually happy to refer.

Present this as a natural step, not optional busywork:

> "Before you hit submit, it's worth checking if you know anyone at [Company]. A referral gets your resume flagged internally and usually means a real human reads it instead of just the ATS. Most companies pay their employees $2-10K for a successful referral, so people genuinely want to help."

**Offer these options:**

1. **Check LinkedIn connections**: "Want me to search your LinkedIn connections at [Company]? I can check 1st and 2nd degree connections."
   - If the `linkedin-personal-branding` skill is installed, use its browser tools to check the user's connections at the target company
   - Otherwise, suggest the user search LinkedIn manually: `site:linkedin.com/in "[Company Name]"` plus their connections

2. **Draft a network ask**: "Want me to draft a quick message you can drop in a group chat or send to your network? Something like 'Hey, anyone know someone at [Company]? Looking at a [Role Title] role there.'"
   - Keep it casual and short. No one reads a paragraph in a group chat.
   - Offer both a group chat version (brief, casual) and a direct message version (slightly more context)
   - Example group chat: "Anyone know someone at [Company]? They have a [Role] opening that's a great fit. Happy to share details if someone can connect me."
   - Example direct message: "Hey [Name], I saw [Company] has a [Role] opening that lines up with what I've been doing at [Current/Recent Company]. Any chance you know someone there who could pass along my resume? Most companies have referral bonuses so it's a win-win."

3. **Check if anyone in their pipeline tracker has connections**: Look at companies they've already applied to or been in contact with. People at those companies may know people at the new target.

**Track referral outreach in the pipeline notes.** When updating `state/jobs.md`, add a note like "Referral: asked in [group/channel], messaged [Name]" so they remember what they've already tried.

If the user wants to skip the referral check and apply directly, that's fine. Don't push. But always surface it as the recommended first step.

### 7. Log Activities

After the scan completes and any pipeline updates are made, log to `state/activity-log.md`.

**If the file doesn't exist, create it with the standard header** (see SKILL.md "Activity Logging" section for format).

**Always log the scan itself:**

```
| {YYYY-MM-DD} | Job search scan | Multiple | - | Scanned {N} companies, {X} new matches found |
```

**If the user applied to a role (added to pipeline as "Applied"):**

```
| {YYYY-MM-DD} | Applied | {Company} | {Role} | {Brief note: referral, tailored resume, etc.} |
```

**If the user moved a role to Interviews stage:**

```
| {YYYY-MM-DD} | Interview scheduled | {Company} | {Role} | {Stage and date if known} |
```

Log each discrete activity as its own row. A scan that results in two applications = three rows (one scan + two applications).

---

### 8. Optional: LinkedIn Search

If the user has BrightData configured and wants LinkedIn results, run the LinkedIn search using the `linkedin-jobs` skill with queries from the watchlist config.
