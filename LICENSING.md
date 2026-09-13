# Image licensing — ACTION REQUIRED BEFORE PUBLISHING

Every image in `assets/img/` was extracted from the source slide deck
(`RR Usability Testing - Screening`). **None of them have documented licences.**
Please confirm the rights for each one before making this repository public or
putting the site in front of participants.

Publishing a GitHub Pages site makes these images publicly accessible, and
GitHub Pages repositories are public by default.

## ⚠️ Known copyright notices visible in the images

These three carry a visible credit or copyright line burned into the image
itself. They almost certainly require permission or removal:

| File | Notice visible in the image |
| --- | --- |
| `mri-diagram.jpg` | "© MAYO FOUNDATION FOR MEDICAL EDUCATION AND RESEARCH. ALL RIGHTS RESERVED." |
| `biopsy-diagram.jpg` | "© MAYO FOUNDATION FOR MEDICAL EDUCATION AND RESEARCH. ALL RIGHTS RESERVED." |
| `mri-step-positioning.jpg` | A photographer/contributor credit line along the bottom edge |

## Full inventory

| File | Where it is used | Appears to be |
| --- | --- | --- |
| `smoke-detector.jpg` | Ch 1, slide 1 | Stock illustration |
| `balance-scale.jpg` | Ch 1, slide 2 | Clip art |
| `burnt-cookies.jpg` | Ch 1, slide 3 | Stock illustration |
| `airplane.jpg` | Ch 1, slide 4 | Clip art |
| `mammogram-illustration.jpg` | Ch 1, slide 4 | Stock illustration |
| `type-mammogram-3d.jpg` | Ch 2, slide 1 | Stock illustration |
| `type-ultrasound.jpg` | Ch 2, slide 1 | Stock illustration (canvas padded to a square with its own background colour; artwork unchanged) |
| `type-mri.jpg` | Ch 2, slide 1 | Stock illustration |
| `mammogram-diagram.jpg` | Ch 2, slide 2 | Medical illustration |
| `mammo-step-preparation.jpg` | Ch 2, slide 3 | Clip art |
| `mammo-step-positioning.jpg` | Ch 2, slide 3 | **Stock photograph of identifiable people** |
| `mammo-step-imaging.jpg` | Ch 2, slide 3 | Stock illustration |
| `ultrasound-exam.jpg` | Ch 2, slide 4 | **Photograph of an identifiable person** |
| `mri-diagram.jpg` | Ch 2, slide 5 | **Mayo Foundation © — see above** |
| `mri-step-preparation.jpg` | Ch 2, slide 6 | Stock illustration |
| `mri-step-positioning.jpg` | Ch 2, slide 6 | **Photograph with credit line — see above** |
| `mri-step-imaging.jpg` | Ch 2, slide 6 | **Photograph of an identifiable person** |
| `biopsy-diagram.jpg` | Ch 2, slide 9 | **Mayo Foundation © — see above** |

`favicon.svg` was written for this project and carries no third-party rights.

The Raleway font in `assets/fonts/` is self-hosted under the SIL Open Font
License 1.1 (`assets/fonts/OFL.txt`), which permits redistribution. Nothing to
clear there.

Two emoji glyphs in the original deck (a green check and a warning triangle)
were **not** carried over — they are reproduced with text and CSS instead, so
there is nothing to clear for them.

## Replacing an image

1. Drop the cleared replacement into `assets/img/` using the same filename, or
   a new one.
2. If you used a new filename, update the matching `src` in
   `content/screening.json`.
3. Run `python3 build.py` and commit the regenerated HTML.
