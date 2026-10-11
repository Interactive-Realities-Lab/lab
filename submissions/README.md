# Submit your lab website information

Edit Markdown in GitHub using your browser, then send one pull request for a maintainer to review. No local software or YAML editing is needed. A submission appears on the website only after maintainer processing. This repository is public; submit only material intended for public use.

**Start here:** [Screenshot guide (PDF)](guide/IRLab-Submission-Guide.pdf). Use the written instructions below for quick reference.

## Find your profile

Each member already has a `profile.md`. Edit the same file for your first submission and every later profile update.

| Member | Student level |
| --- | --- |
| [Tanim Ahmed](members/tanim-ahmed/profile.md) | PhD student |
| [Jie Ding](members/jie-ding/profile.md) | PhD student |
| [Keivan Sabet](members/keivan-sabet/profile.md) | PhD student |
| [Shakrin Jahan Mozumder](members/shakrin-jahan-mozumder/profile.md) | PhD student |
| [Rafid Mostafiz](members/rafid-mostafiz/profile.md) | PhD student |
| [Jai Sai Naga Venkat Guttikonda](members/jai-sai-naga-venkat-guttikonda/profile.md) | PhD student |
| [Fahmida Imrose](members/fahmida-imrose/profile.md) | PhD student |
| [Jessica Anioha](members/jessica-anioha/profile.md) | Master's student |
| [Ethen Santana](members/ethen-santana/profile.md) | Undergraduate student |
| [Labibah Zainab](members/labibah-zainab/profile.md) | Undergraduate student |

## First time: make your own fork

1. Sign in to GitHub and open [Interactive-Realities-Lab/lab](https://github.com/Interactive-Realities-Lab/lab). Expected result: owner `Interactive-Realities-Lab`, repository `lab`.
2. Click **Fork**, then **Create a new fork** if shown. Choose your own username as **Owner**, keep repository name `lab`, and click **Create fork**. Expected result: repository `YOUR-USERNAME/lab`.
3. Select **main** in the branch menu. Expected result: your own fork shows its `main` branch. Use this branch for all edits and uploads below.

## Already have a fork: prepare for a later request

1. If your previous pull request is still open, continue editing its source branch in your own fork. Expected result: new commits update that request automatically. Do not open another request while it is pending.
2. After your previous request is merged, open `YOUR-USERNAME/lab`, select **main**, click **Sync fork**, then **Update branch** if offered. Expected result: your fork is up to date with `Interactive-Realities-Lab/lab:main`.
3. If GitHub reports conflicts or offers to discard commits, keep your unsynced work and ask the maintainer for help. Expected result: your work remains available to resolve.

## Edit your profile

1. In your own fork on **main**, open **submissions → members → your folder → profile.md**. Identify your folder using the table above. Expected result: the page owner is your own username. Links viewed in the lab repository lead to the lab repository; check the owner before editing.
2. Click the pencil icon (**Edit this file**). Enter a 50–80 word English biography, 3–5 research interests, and your current IRLab project(s) with a brief contribution. If no project is assigned, write **Not yet assigned**. Upload a profile photo for your first profile; replacements are optional for already published profiles. Replace bracketed prompts and remove unused optional sections. Expected result: the editor contains your proposed profile.
3. Click **Commit changes…**, enter a short description, choose **Commit directly to the main branch**, and click **Commit changes**. Expected result: your fork displays your updated file. Commit each file edit this way.

## Add a project, publication, or news item

Templates: [Profile](templates/profile.md), [Project](templates/project.md), [Publication](templates/publication.md), [News](templates/news.md). The profile template is a reference; edit your existing `profile.md` for profile updates.

1. Open the relevant template, click **Raw**, and copy its text. Expected result: copied plain Markdown without GitHub page controls.
2. Return to your own fork on **main**, open your member folder, and click **Add file → Create new file**. Expected result: the editor is inside `submissions/members/your-folder/`.
3. Name the file `project-topic.md`, `publication-topic.md`, or `news-topic.md`, using a descriptive topic, such as `project-survivors.md`. Paste the template and replace its prompts. Expected result: a factual English draft; choose the actual verified publication status (**unpublished draft**, **preprint**, **accepted**, or **published**). The template defaults to **not yet confirmed** until verified; already published papers should use **published** when confirmed.
4. Click **Commit changes…**, choose **Commit directly to the main branch**, and click **Commit changes**. Expected result: the new file appears in your member folder. Later corrections edit that same topic file.

## Upload a photo or attachment

1. In your own fork on **main**, open your member folder and click **Add file → Upload files**. Select or drag your files into the upload area. Expected result: GitHub lists the files.
2. Keep each file's real extension. Photos can be `.jpg`, `.png`, or `.webp`; conversion is not required. Use a descriptive filename such as `portrait.jpg`. Expected result: your photo keeps its actual format.
3. Click **Commit changes** to commit the upload to **main**. Expected result: uploaded files appear beside your `profile.md`.
4. Edit the relevant Markdown file, enter the relative filename such as `portrait.jpg`, and **Commit changes** again. Expected result: the submission identifies the file without a local computer path.

## Send one pull request

1. After committing all edits and uploads, open your fork's repository page and click **Contribute → Open pull request**, or **Compare & pull request** if offered. Expected result: GitHub shows a comparison of your commits.
2. Check **base repository: Interactive-Realities-Lab/lab**, **base: main**, **head repository: YOUR-USERNAME/lab**, and **compare: main**. Review **Files changed**. Expected result: the request includes your intended submission files.
3. Click **Create pull request**, enter a clear title and description, leave **Allow edits by maintainers** checked if offered, and click **Create pull request**. Expected result: an **Open** pull request with a number, such as **#12**.
4. Your submission is complete when you see **Open pull request #…**. Wait for review; you do not need to click **Merge**. For requested corrections, edit and commit the same files on the same source branch in your fork. Expected result: the existing request updates automatically.

Maintainers: see [MAINTAINERS.md](MAINTAINERS.md).
