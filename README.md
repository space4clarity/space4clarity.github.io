# Space4Clarity

Personal blog hosted with GitHub Pages: https://space4clarity.github.io/

Daily Reading automatically selects a passage from a cached Project Gutenberg book,
generates a 500–800-word reflection, verifies its quotation and structure, obtains a
separate AI editorial check, and publishes one post per America/Denver calendar day.
The homepage, archive, and RSS feed update with each post. The site contains the
Daily Reading series; generated entries disclose AI authorship.

## Run locally

Requires Python 3.11+, timezone data (`tzdata` on Windows), Node.js, Git, and a signed-in
Codex CLI (`codex login status`). Codex usage draws on that account's allowance;
no new paid API service or API key is configured by this project.

```powershell
python .automation/daily.py --download-library
python .automation/daily.py
python .automation/daily.py --check
python .automation/daily.py --publish
```

Generation runs in Codex's read-only sandbox with no tools requested. The Python
script escapes all generated text before rendering HTML and controls publishing.
The four starter titles and first-post themes are in `.automation/books.json`.
On subsequent visits it samples unused passages and avoids recent topics.
Downloaded ebooks retain their complete Gutenberg headers/licenses in the ignored
cache; published posts link to each book's landing page. Downloads use mirrors
listed at https://www.gutenberg.org/MIRRORS.ALL rather than scraping the main site.

## Daily schedule on Windows

```powershell
powershell -NoProfile -File .automation/install-schedule.ps1 -Time 08:17
```

The task runs daily at 08:17 in the Windows system timezone and at sign-in, under
the current user's existing identity with limited privileges. The machine must be
on and the user signed in. Missed runs start when available. It retries failures
twice, 20 minutes apart. A date check prevents duplicate posts; a failed push is
retried without regenerating that day's entry. The process never force-pushes.
Authentication expiry or exhausted AI usage requires restoring account access.

Inspect results in Windows Task Scheduler under **Space4Clarity Daily Reading**.
Logs and generated source/review records are in `.automation/runs/` (not committed).

```powershell
Get-ScheduledTaskInfo -TaskName 'Space4Clarity Daily Reading'
Disable-ScheduledTask -TaskName 'Space4Clarity Daily Reading'
```

This checkout is a dedicated automation working copy. Make unrelated site edits in
another checkout. The runner pulls remote updates only when clean, and stops on
conflicts or unrelated edits. Books are source material, never executable input.
Quote verification is exact after whitespace normalization; semantic checking is
AI-based and cannot guarantee interpretive or factual correctness. Failed checks
stop publication rather than substituting an unchecked filler article.
