# Changelog

## 2026-11-05
- Skills: built-in line icons for all 13 skills (CMS "Built-in icon" select); uploaded official icons override them on a white tile; monogram fallback kept.
- Projects: GitHub repository + Live Demo links per project; card image opens the repository with a "View repository" hint; invalid links fail the build.
- Other Projects: lists published non-featured projects and the GitHub profile button; hidden when both are empty.
- Pages CMS: projects/skills sorted by order, searchable, list columns, status labels (Published / Draft hidden / Archived hidden), validation patterns for IDs, slugs and URLs, rename disabled (file name = stable ID).
- Data: TaskFlow Pro live demo verified and enabled. Smart Design Pro live URL returned 404 and stays hidden.
- Responsive: tablet layout with desktop navigation at 768px, desktop layout from 1024px, phone fixes (hero sizing, 44px touch targets, stacked buttons, icon-only menu under 360px, outside-tap close), no horizontal scroll at 320-1920px.
- Tests: 7 new test groups (icons, links, Other Projects, ordering/hide/delete, CMS schema, breakpoint sync).
