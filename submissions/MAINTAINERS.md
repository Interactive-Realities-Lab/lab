# Maintainer intake

Markdown under `submissions/` is the member's canonical intake record. Maintainers manually review it and map approved information into the website's existing structure. There is no bot or automatic publication workflow.

1. Review the pull request and attachments. Confirm names, student levels, roles, biographies, links, dates, contributions, and publication statuses. Request corrections in the same open pull request. Any factual correction made during intake must also update the source submission Markdown in that same pull request, so the intake record and website agree.
2. Check completeness before publishing: confirm a 50–80 word English biography, 3–5 research interests, current IRLab project names and brief contributions (or **Not yet assigned**), and a first-profile photo. Replacement photos are optional for existing published profiles. No bracketed prompts, template placeholders, guessed programs, or unresolved facts may appear publicly on the website. Remove unused optional fields. Incomplete new profiles remain intake drafts; precreated folders alone do not create public people entries.
3. Manually map approved material using the existing site conventions:

| Intake | Website destination |
| --- | --- |
| `members/<slug>/profile.md` | `data/authors/<slug>.yaml` for author data and `content/authors/<slug>/_index.md` for profile content |
| Member photo | `assets/media/authors/`, referenced from author data and profile content |
| `project-topic.md` | Appropriate existing or new `content/projects/` record and established image assets |
| `publication-topic.md` | Appropriate `content/publications/` record with confirmed citation metadata, bibliography, and supported attachments |
| `news-topic.md` | Appropriate `content/news/` record with confirmed date and established assets |

4. For people entries, preserve confirmed student levels and use the existing grouping convention: `PhD Students`, `Master's Students`, or `Undergraduate Students`. For each new member, also update the appropriate group members list in `content/people.md`; confirm that the People card and profile destination render correctly. Check the current people rendering and configuration when adding an entry. Use the existing author schema; intake Markdown itself is not site content.
5. Keep **unpublished draft** and **not yet confirmed** publications as intake drafts. Verify the actual status of every record, including already published papers. Create public publication entries only when their actual status and public citation material are confirmed and approved. Do not infer acceptance or publication from a title or year.
6. Preserve supported photo formats or process them as needed for the website. Members do not need to convert their photos. Check asset references resolve.
7. Review the rendered website and final diff. Merge through the normal maintainer process when approved source records and website content agree. Tell the member whether the request was merged and whether website publication was verified; merging alone does not establish deployment.

Retain the same `profile.md` and topic files for later corrections. New submissions and corrections follow this manual intake process.
