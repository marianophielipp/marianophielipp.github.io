# Mariano Phielipp - Professional Website

This is the source code for my professional website hosted at [marianophielipp.github.io](https://marianophielipp.github.io).

## About

Dr. Mariano Phielipp is a Director of Embodied Intelligence, specializing in Deep Learning, Reinforcement Learning, Machine Learning, and Artificial Intelligence. His research focuses on robotics, computer vision, natural language processing, and AI for Science.

## Website Structure

- **Homepage** (`index.html`) - Main landing page with latest updates
- **Bio** (`bio.html`) - Professional biography and background
- **Research** (`research.html`) - Research areas and publications
- **Assets** - CSS, JavaScript, and image files

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

- **Navigation/footer changes:** Update header, menu, sidebar, and footer in every HTML file (index, bio, research, contact, publications, 404) so they stay in sync. A future refactor to a static site generator (e.g. Jekyll) with shared includes would reduce this duplication; see `AUDIT.md`.

## Contact

- LinkedIn: [mariano-phielipp-941624](https://www.linkedin.com/in/mariano-phielipp-941624/)
- Twitter: [@mphielipp](https://x.com/mphielipp)
- Email: mphielipp@gmail.com
