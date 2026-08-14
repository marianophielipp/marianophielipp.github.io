# Mariano Phielipp - Professional Website

This is the source code for my professional website hosted at [marianophielipp.github.io](https://marianophielipp.github.io).

## About

Dr. Mariano Phielipp is a Director of Embodied Intelligence, specializing in Deep Learning, Reinforcement Learning, Machine Learning, and Artificial Intelligence. His research focuses on robotics, computer vision, natural language processing, and AI for Science.

## Website Structure

Four sections, one vocabulary. The same labels are used in the header, the mobile
menu panel, the prev/next footer and the sidebar.

- **Home** (`index.html`) — positioning and three selected pieces of work
- **About** (`bio.html`) — background, roles, education, awards, patents
- **Research** (`research.html`) — research themes
- **Publications & Patents** (`publications.html`) — searchable record driven by `data.json`
- **CV** (`cv-mariano-phielipp.pdf`) — full curriculum vitae
- **Contact** (`contact.html`) — reachable from the header action, not a peer section
- **404** (`404.html`)

Reading order for prev/next: Home -> About -> Research -> Publications -> Contact.

## Publications data

The live site reads only `data.json` at the repo root. `scripts/gscholar.py`
fetches from Google Scholar and `scripts/clean_publications.py` normalises it into
`_data/`; `data.json` is the published result. Patent entries carry their US number
and filing status, verified against USPTO and Google Patents records.

`scripts/check_patents.py` fails if the patent list in `bio.html` and the patent
entries in `data.json` disagree. Run it after editing either:

```bash
python3 scripts/check_patents.py
```

The count drifted once because the same list was maintained in both places.


## Technologies Used

- HTML5
- CSS3 with responsive design
- JavaScript
- FontAwesome icons
- Based on HTML5 UP "Future Imperfect" template

## Local Development

Due to modern browser CORS (Cross-Origin Resource Sharing) policies, the `publications.html` page must be served over a fast local web server (instead of double-clicking the file locally to open via the `file://` protocol). 

To run the site locally, open a terminal in this directory and run:

```bash
# For Python 3
python -m http.server 8000
```
Then visit `http://localhost:8000` in your web browser.

## Maintenance

- **Navigation/footer changes:** the header, menu panel, sidebar and footer are
  duplicated across all six HTML files and must be edited in every one. They are
  currently byte-identical apart from the `aria-current` marker and the prev/next
  targets — keep them that way. A static site generator with shared includes would
  remove the duplication; the empty `_includes/` and `_layouts/` directories from an
  abandoned attempt have been removed, and `.nojekyll` disables Jekyll on GitHub Pages.
- **Patents:** run `python3 scripts/check_patents.py` after touching `bio.html` or `data.json`.
- **Reviews:** see `AUDIT.md` (March 2026) and the August 2026 review in the project docs.

## Contact

- LinkedIn: [mariano-phielipp](https://www.linkedin.com/in/mariano-phielipp/)
- Twitter: [@mphielipp](https://x.com/mphielipp)
- Email: mphielipp@gmail.com
