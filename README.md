# Shamikh Al-Aofiry portfolio

Static HTML/CSS/vanilla JS, generated from JSON; no runtime CMS or database. The only generated site is `dist/`. The repository's `index.html` and the detail templates are sources, not a complete deployable site: deploy `dist/`, not the repository root. Root-relative paths target the user site `https://shamkh-alafiry.github.io/`; a project-subpath installation needs a configured base path first.

## Structure
- `index.html`, `style.css`, `script.js`: homepage source template, shared design, and navigation/menu/scroll-reveal behavior. The site is English-only (`lang="en"`, `dir="ltr"`). The build fills every `data-field` and `<!-- slot:... -->` marker in `index.html` from the JSON data.
- `projects/index.html`, `skills/index.html`: build-time reusable detail templates.
- `data/profile.json`, `education.json`, `certificates.json`: structured records; the certificate array starts empty. The unused `photography.json` file is retained but is not used or published.
- `data/projects/*.json`, `data/skills/*.json`: one file per item. The project's `skills` array is the single source of relationship IDs; the build derives the reverse links.
- `media/profile`, `projects`, `skills`, `certificates`, `cv`, `documents`: uploaded files. Empty directories are not tracked by Git; create them if necessary or let the CMS create them on upload.
- `.pages.yml`: Pages CMS configuration (JSON syntax is valid YAML). `tools/build.py`: dependency-free Python build. `.github/workflows/publish.yml`: manual GitHub Pages deployment.
- `dist/`: generated output, not source. Only published projects, skills, certificates and referenced media are deployed.

## Configure Pages CMS
1. Push the source files to your own GitHub repository. Create a `review` branch from `main`. Keep secrets, private photos and unpublished confidential information out of the repository: if the repo is public, every branch is public.
2. In GitHub Settings → Pages, set Source to **GitHub Actions**, not branch/root. Install the GitHub App for Pages CMS at https://app.pagescms.org/ and grant it only the required repository access. Open the repository and `review` branch. The CMS reads `.pages.yml` on that branch.
3. Edit through the labelled sections. Use `draft` until content is ready. Saving in the CMS writes Git commits; it is not by itself an approval or deployment. Branch and CMS permissions must be configured by the repository owner. Test the actual UI on your account before relying on it.
4. Open a GitHub pull request from `review` into `main`, inspect its changes, and merge only after your approval. Configure branch protection/rulesets to prevent bypasses when your plan allows it. Then run **Publish reviewed portfolio** manually from Actions on `main`. Set up `github-pages` environment protection/reviewers if your GitHub plan supports them. If environment approval is unavailable, the manual dispatch is the explicit deployment approval; account owners with privileges can bypass process unless branch/access controls prevent it.
5. The workflow runs `python tools/build.py`, uploads only `dist/`, and deploys that artifact. Confirm Pages is using Actions; a branch-root Pages source would publish unfiltered data and media. Public repository source/PRs are still public even with a filtered Pages artifact.

## Manage projects in Pages CMS
The Projects list in the CMS is sorted by Display order and shows name, status, order, Featured and stage, with search by name/summary.
- **Add**: New entry. Fill ID and slug (validated: lowercase letters, digits, hyphens), name, status, order.
- **Edit**: open the entry and save. Every save is a Git commit on `review`.
- **Hide**: set status to Draft or Archived. The project, its page, its JSON and its media disappear from the built site; nothing is deleted.
- **Delete**: use the CMS Delete action to remove the file permanently (renaming files is disabled because the file name is the stable ID).
- **Order**: lower Display order appears first. Use gaps (10, 20, 30) so you can insert projects later without renumbering.
- **Featured on**: large card in Portfolio. **Featured off**: compact entry under Other Projects (still published, still has its details page).
- **GitHub repository URL** (`https://github.com/user/repo`): the card image opens the repository (with a "View repository" hint) and a GitHub Repository button appears on the card and details page. Leave empty to hide both.
- **Live demo URL**: shown as a Live Demo button only after "Live demo checked and available" is enabled. The build fails if a published project has a non-https link, or the box is checked with no URL, so typos never ship silently.

## Add or edit a project (details)
In Projects, create an entry. Choose a stable lowercase ID and unique URL slug using letters, digits and hyphens. Fill the English text fields, select `draft`/`published`/`archived`, set display order and Featured. Enter real descriptions and select planned/implemented/verified for each feature and technology. Optionally set a short context label (e.g. Graduation project) and a stage badge. Upload a cover or screenshots; add evidence and links only when genuine. Without a cover, the card shows labelled conceptual artwork, never a fake screenshot. Setting `github_url` makes the card image link to the repository and adds a GitHub Repository button; no redesign needed. Technologies marked planned are always shown under Planned technologies, never as implemented. A live-demo link remains hidden until you check the URL and enable “Live demo checked and available”. Set published when reviewed, then follow the PR and manual deploy process. URL: `/projects/<slug>/`. Changing a slug breaks old URLs: plan redirects separately.

## Add or edit a skill and relationships
Create an entry in Skills with a unique stable ID and slug, names, optional description, an icon and actual experience/evidence. Icon priority: an uploaded official icon (shown on a white tile so brand colours stay accurate) > the "Built-in icon" select (generic line glyphs drawn for this site in the same style as the other icons; they are not official trademarks) > a text monogram. Only upload logos you are allowed to use. Set order and status. In Projects, select related skills using the reference picker. The project record stores IDs once; the generator places links on both project and skill pages. Unpublished skills or projects do not generate public links. Renaming an ID can break references and fails the build; keep IDs stable. Deleting a referenced skill requires removing its project references first.

## Files, images, resume and other content
Use named media folders in the CMS. Attach evidence via the relevant entry; only files referenced by published content are copied into the output. Screenshots and conceptual covers must be labeled honestly. Captions and detailed alternative text are limited in the current project image field; improve the schema before relying on complex image descriptions. For the résumé, upload the PDF, review it manually, and check `Resume manually verified`; the build also checks a PDF header, minimum size and EOF marker. Those basic checks do not prove the résumé is complete or that the PDF is valid. If unchecked, no résumé is published and the hero shows no Download Resume button. Set `github` in Profile to show the Other Projects section (Explore GitHub Projects) and the GitHub contact icon; both stay hidden while it is empty. Set `profile_image` to replace the SA monogram in the hero with your real portrait. In Certificates, add real entries, mark published, and deploy. No records have been invented.

## Responsive design
One stylesheet serves every screen; there is no separate mobile site. Breakpoints: 1024px and up desktop, 768-1023px tablet (desktop navigation, tighter grids), under 768px phone (menu button, single-column layout, 44px touch targets), under 480px small phone (stacked card buttons), under 360px very small phone (icon-only menu button, one skill per row). The phone breakpoint is defined once in `style.css` and mirrored by `MOBILE_QUERY` in `script.js`; the tests fail if they drift. The mobile menu closes on link tap, outside tap and Escape. Checked at 320, 375, 390, 430, 768, 1024, 1366 and 1920px in headless Chromium: no horizontal scrolling, no console errors, no broken files.

## Local preview and tests
Requires Python 3.9+ (CI uses 3.12). From the repository root:

```
python tools/build.py
python tests/test_build.py
python -m http.server 8000 --directory dist
```

Open `http://localhost:8000/`. Direct pages such as `/projects/nims/` and `/skills/cisco/` are static files, so they survive reload. Unknown routes produce a server 404; `dist/404.html` is the intended GitHub Pages custom error page. Its actual status and display must be checked on the deployed site. Avoid opening source HTML directly: it does not run the build and uses absolute site-root URLs.

Content is rendered as static English HTML at build time; JavaScript only adds the active-section highlight, the mobile menu and a one-time scroll reveal, and all content stays visible without it. Motion respects `prefers-reduced-motion`. The build fails if non-English script, leftover bilingual `{en, ar}` objects or unfilled template markers reach the output. Search engine and social sharing behavior have not been verified. No custom SEO images or canonical URLs are claimed.

The CMS schema was matched against https://pagescms.org/docs/configuration/ but was not exercised in an authenticated Pages CMS session. The GitHub workflow, branch protection and publication have not been tested in the actual repository. Treat all production setup and security enforcement as unverified until tested there.
