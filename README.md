# Schwerman Plumbing — independent website proposal

A 19-page static HTML/CSS/JavaScript redesign based on the responsive structure of the Firefly HVAC template, with Schwerman-specific research, plumbing imagery, teal/honey colors, local service content and structured data. **Not yet approved by Schwerman Plumbing.** See `RESEARCH.md`, `SEO.md` and `ASSETS.md` for claims, search intent and image provenance.

## Public owner preview (GitHub Pages)

1. In the GitHub repository, open **Settings → Pages**.
2. Select **Deploy from a branch**, then **`main` / `/docs`** and Save.
3. Open the Pages URL after the build finishes. The default preview base is `https://andrianventures.github.io/schwerman-plumbing-redesign/`.

This preview intentionally sets `<meta name="robots" content="noindex,nofollow">` on every page. It should not be indexed or substituted for the owner's official site until the business approves it. A public GitHub repository is readable by anyone; do not commit private contact submissions, secrets, or business-only photos.

## Contact-form behavior — important

**On static GitHub Pages:** The primary form validates required fields and opens a prefilled **email draft** to the business's published email. The visitor **must press Send in the email app**. There are also buttons to prepare a **text draft** and to **copy the request**. GitHub Pages alone cannot automatically submit or store a form, and opening an app is not proof of delivery. For urgent problems, use the prominent phone link. No third-party form integration is required for these visitor-controlled options.

**On a Node-capable host:** The bundled dependency-free `server.mjs` serves the same pages and saves valid enquiries to a private JSONL file, with a password-protected `/owner/inbox` readback. No third-party integration is needed; there are **no automatic email alerts**. Use HTTPS, a persistent filesystem, backups, controlled access, and a real owner's approved privacy policy before collecting live data. The server is not runnable on GitHub Pages.

```sh
export SCHWERMAN_ADMIN_PASSWORD='generate-a-unique-long-secret-outside-the-repo'
export SCHWERMAN_BASE='https://your-node-host.example/'
python3 build.py
PORT=8080 HOST=127.0.0.1 node server.mjs
```

Set `SCHWERMAN_DATA_DIR` if a different private storage directory is needed. Do not put it under `docs/`, commit it or expose the inbox publicly without HTTPS. Only one Node process should append to the JSONL file at a time; for scaled hosting, replace it with a durable database.

## Editing and release

- Edit page-specific content in `content.py` and layout/schema in `build.py`, then run `python3 build.py`.
- The repository includes the generated `docs/` tree so Pages needs no build step.
- Set `SCHWERMAN_BASE` to the final approved domain before rebuilding. Verify canonical URLs, sitemap, schema, images, services and contact details, then remove preview-only noindex on the final domain (the generator does this for non-preview HTTPS bases). Privacy and accessibility drafts remain noindex pending approval.
- Do not invent Google reviews, licenses, warranties, emergency response times or claims the owner hasn't verified.
