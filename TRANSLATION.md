# Spanish version — review notes

The site is bilingual: English at the site root, Spanish under `/es/`. Each
language is a separate content file (`content/screening.en.json`,
`content/screening.es.json`) rendered into its own tree, with a toggle in the
header linking each page to its counterpart.

Spanish slide text is transcribed **verbatim** from the Spanish deck
(`Copy Spanish Real Risk slides`), the same approach used for the English deck.
Two things need a human eye before this goes in front of participants.

## 1. The two decks disagree on some medical content

These are not translation choices — the two source decks say different things.
Each language currently shows what its own deck says. **A clinician should
decide which is correct and whether both languages should match.**

| Where | English deck | Spanish deck |
| --- | --- | --- |
| False Positives (Ch 1) | "For women who got **MRIs**, 10 out of 100 patients will need further testing" | "Aproximadamente 10 de cada 100 **mamografías** muestran alguna anomalía" |
| Comparison table (Ch 2) | 3 test columns | 4 columns — adds **Mamografía con Contraste** (contrast-enhanced mammography) |
| Comparison table — MRI time | "15 min prep + 15-20 min in machine" | "15-20 min" (the prep wording sits in the contrast-mammography column instead) |
| Comparison table — MRI cost | `$$$$` | `$$$$`, with contrast mammography at `$$$` |
| Breast MRI (Ch 2) | "for women at high risk **and with dense breasts**" | "en mujeres con alto riesgo" (dense breasts not mentioned) |
| Risk Categories — average | "No personal history of breast cancer **or atypia on biopsy**" | "Sin antecedentes personales de cáncer de seno" |
| Risk Categories — high | "Have had a breast biopsy **with atypia**" | "Resultados de biopsias mamarias **benignas de alto riesgo**" |
| Risk Categories — high | "lifetime risk of about **20-25% or greater**" | "mayor a **20 de cada 100** personas" |
| Risk Categories — high | gene change and family history are **two separate** criteria | combined into **one** criterion |
| Why do we screen (Ch 1) | 4 bullets | 3 bullets — omits "This is why regular breast cancer screening is so important" |
| Mammogram steps (Ch 2) | includes "They may reposition you" | omits it |
| Breast MRI steps (Ch 2) | includes "A safety button is provided to press if needed" | omits it |
| Biopsy results (Ch 2) | "5-10 **business** days" | "5-10 días o más" |
| Ch 3 questions 1 and 2 | "average risk **women**" | "la mayoría de **las personas**" / "**las personas**" |

## 2. Content I translated myself — needs a fluent review

Two slides have **no Spanish source** in your deck. I wrote the Spanish for
them. Both are marked `"translated": true` in `content/screening.es.json`, so
you can find them with:

```bash
grep -n '"translated"' content/screening.es.json
```

- **`Preguntas para hacerle a su médico`** — 2 questions.
- **`¿Qué es lo más importante para usted?`** — the slider tool: 5 dimensions
  × (title, both endpoint labels, 9 framings, 9 summary lines), plus the intro,
  the disclaimer and the summary heading. This is the bulk of the
  machine-translated text and the part most worth reading closely, since it
  speaks to the reader about their own preferences.

All **interface** strings are also mine (navigation, buttons, the progress
sidebar, the reveal button, slider announcements). They live under `ui` in each
content file.

## 3. Smaller deviations from verbatim

Two places where I did not copy the Spanish deck exactly:

- **Slide title.** Page 3 of the Spanish deck is headed "Benefits and Potential
  Harms of Screening" — still in English. I rendered it as "Beneficios y
  Posibles Daños de la Detección", since an English heading on a Spanish slide
  looked like an oversight rather than a choice.
- **"40 aňos".** Pages 20–21 use `ň` where `ñ` is meant. Rendered as "años".

One typo I did **not** fix, so you can decide: page 13's callout reads "Tiempo
dentro del túnel de la RM 15-20 **minutes**" — the English word, kept verbatim.

## Adding or editing Spanish content

Both content files must describe the same chapters, the same number of slides,
and the same number of menu entries — otherwise a toggle would land on a
missing page. `build.py` refuses to build if they drift apart, naming the
mismatch.
