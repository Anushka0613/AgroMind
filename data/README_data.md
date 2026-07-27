# Data notes

- `crop_recommendation.csv` — primary dataset used for both the crop model
  and the derived per-crop nutrient profiles (2200 rows, 22 crops).
- `fertilizer_prediction.csv` — a public fertilizer dataset explored during
  research but NOT used in the final system: it only covers 2 crop types
  (rice, coconut), too narrow for our 22-crop system. Kept here for
  reference only. See README.md section 2 for why we built a rule-based
  fertilizer advisor from crop_recommendation.csv instead.
