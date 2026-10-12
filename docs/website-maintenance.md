# Website maintenance

Review member pull requests and keep approved submission records consistent with the website. Confirm names, roles, biography, interests, project contributions, dates, links, attachments, and publication status. Correct intake facts in the same pull request before publishing.

| Submission | Website destination |
| --- | --- |
| `submissions/members/<slug>/profile.md` | `data/authors/<slug>.yaml` and `content/authors/<slug>/_index.md` |
| Profile photo | `assets/media/authors/`, referenced by the author record and profile |
| Project item in `updates.md` | `content/projects/` and established image assets |
| Paper item in `updates.md` | `content/publications/`, confirmed citation metadata, bibliography, and supported attachments |
| News item in `updates.md` | `content/news/` and established assets |

Before publishing a new profile, check its 50–80 word English biography, 3–5 interests, current IRLab projects and contribution (or **Not yet assigned**), and photo. Remove prompts and unresolved facts. Use the existing author schema and **PhD Students**, **Master's Students**, or **Undergraduate Students** grouping; update the matching list in `content/people.md`. Precreated submission folders do not create public profiles.

Keep unpublished or unconfirmed papers as intake drafts until status and public citation material are verified. Preserve supported photo formats and check asset references. Review the rendered People card, profile, affected pages, and final diff before merging. Report merge status and whether website publication was verified.

Members retain the same `profile.md` and `updates.md` for future edits. Approved Markdown is mapped manually to the website.
