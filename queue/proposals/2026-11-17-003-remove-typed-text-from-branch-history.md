---
id: 2026-11-17-003
from: agent (Fetch, san-francisco, 311 plan step 2)
needs: supervisor decision
problem_relieved: A commit on the pushed branch contains a file with typed text from a category field, which should not be in the repository.
---

# Should the branch history be rewritten to remove commit `ae2bdf6`'s taxonomy file?

## What is in the history

Commit `ae2bdf6` added `sources/ea7ad512634f8515b459ba732044ee8738b298967f1a26a8f14d19e44dba95e2.json` and was pushed to `origin/claude/peaceful-cannon-w8prs2`. It is a grouped count of 311 cases by service name and subtype, with 826 distinct subtype values. Most are controlled categories. A few families hold typed text: 188 labels of the form "Construction Zone Tow-away Permits for [applicant]" (about 86 look like organizations, most of the rest like agency or company acronyms) and 49 `Shared Spaces Violation` subtypes. I have not read the names, so I cannot say that none is an individual. Each label stands for 10 or more cases; none is a single record. The file was removed in the next commit, but it stays reachable in history.

## Why it happened

My safety gate printed a warning and did not stop the commit, because I chained the commit after it. The full account is in `cities/san-francisco/notes.md`, under "Incident". The fetcher now holds responses like this one, and a test covers it.

## Options

**A. Rewrite the branch (recommended if the repository is shared or public).** I would reset the branch to the commit before `ae2bdf6`, re-apply the later work without the file, and force-push. This needs your approval, since a force-push rewrites a published branch. Hosting services can keep unreachable commits for some time, so it reduces the exposure and does not guarantee removal; if that matters, the host's support can purge it.

**B. Leave it.** If the repository is private, the labels are mostly organization names and each stands for 10 or more cases, the exposure may be acceptable. The file is no longer in the tree.

**C. Review first.** You or I read the 188 applicant labels to see whether any is an individual's name, and then choose A or B. I would rather you did this than I, to avoid repeating the exposure.

## What I will not do

I will not force-push without your approval, and I will not assume the repository's visibility.

## Status: still open

Not covered by approval `2026-11-17-002`, which approved the other proposals and held this one back. The agent needs two things to act: an explicit instruction to rewrite or leave the history, and whether the repository is private or public.
