# astrosdlu.github.io

Academic homepage for Shengdong Lu.

## Deployment Target

The desired public URL is:

```text
https://astrosdlu.github.io
```

For GitHub Pages, that exact URL requires the site owner to be a GitHub user or
organization named `astrosdlu`, with a repository named `astrosdlu.github.io`.

Recommended setup:

1. Create a GitHub organization named `astrosdlu`.
2. Keep `AstroShengdong` as an owner of that organization.
3. Create the repository `astrosdlu/astrosdlu.github.io`.
4. Upload these files to the repository root.
5. In repository settings, enable GitHub Pages from the `main` branch root.

GitHub Pages documentation: https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages

## Local Files

- `index.html` - homepage content
- `styles.css` - visual design
- `data/publications.json` - ADS-generated publication data used by the homepage
- `scripts/update_publications.py` - weekly ADS public-library metadata updater
- `scripts/generate_research_images.py` - reproducible script for the research-section images
- `assets/shengdong-lu-photo.jpg` - profile image
- `assets/research/*.png` - generated research-section images
- `documents/shengdong-lu-cv.pdf` - CV
- `documents/shengdong-lu-publications.pdf` - publication list

## Publication Updates

The publications section is generated from the ADS public library:

```text
https://ui.adsabs.harvard.edu/public-libraries/Ehu1oU_ISIairGeqwhMJWw
```

Add an `ADS_TOKEN` repository secret in GitHub. The
`.github/workflows/update-publications.yml` workflow runs every Monday and can
also be started manually from GitHub Actions.

## Attribution

The page structure is adapted from Sownak Bose's academic homepage
(https://sownakbose.github.io/), whose source repository is licensed under
Creative Commons Attribution 3.0 Unported.
