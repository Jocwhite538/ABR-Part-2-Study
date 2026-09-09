# ABR Part 2 Study Lab - GitHub Source Edition

Static GitHub Pages version. No Python server is required.

## Upload to GitHub

Put this folder's contents inside your repository, for example:

```
Medical-Physics/
  abr/
    part-2/
      index.html
      styles.css
      app.js
      question_bank.json
      assets/
        source/
        teaching/
```

Then visit:

`https://YOUR-USERNAME.github.io/Medical-Physics/abr/part-2/`

## What is included

- 1,071 questions in six ABR Part 2 categories.
- Exact source crops generated from the uploaded original question packets for source-dependent / visual / table questions.
- 55 structured content-block questions (including responsive HTML tables where available).
- Original source assets take priority over reconstructed teaching figures.
- Browser `localStorage` progress: attempts, accuracy, missed items, flags, sessions.
- Export/import progress JSON for moving progress between browsers/devices.
- CSV export for sessions and filtered question lists.
- Review-required status for unresolved answer/source conflicts.

## Answer-key qualification

The answer keys provided with this project are the primary grading source. Several of those answer keys explicitly state that they were reconstructed from quiz printouts with collapsed solutions. Therefore this app distinguishes software/source-fidelity QA from independent clinical validation of every answer.

One obvious visual/key conflict (Therapy Imaging Q68) is deliberately flagged for manual review rather than silently certified.
