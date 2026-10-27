# Week 11 mutation scripts

Run from the repository root.

| Script | Purpose |
|---|---|
| `summarise_v2.py` | Parse `mutmut_results_v2.txt` into overall/per-module JSON, write `survivors_v2.txt`, and build `v1_vs_v2.csv` |
| `pick_survivors.py` | Group survivors by function and write `survivor_candidates.csv` |
| `compare_survivors.py` | Join v2 survivors to the Week 7 survivor categories (`survivors_v1_v2.csv`) |
| `make_chart.py` | Build `v1_vs_v2.png` from the two summary JSON files |
| `build_excel.py` | Build `week11/Week11_TrackD_Findings.xlsx` (native Excel chart dashboard) |

Example:

```bash
python week11/mutation_v2/scripts/summarise_v2.py \
  week11/mutation_v2/mutmut_results_v2.txt \
  week11/mutation_v2/mutation_v2_summary.json \
  week11/mutation_v2/v1_vs_v2.csv

python week11/mutation_v2/scripts/pick_survivors.py \
  week11/mutation_v2/survivors_v2.txt \
  week11/mutation_v2/survivor_candidates.csv

python week11/mutation_v2/scripts/compare_survivors.py \
  week7/survivor_categories_v1.csv \
  week11/mutation_v2/survivors_v2.txt \
  week11/mutation_v2/survivors_v1_v2.csv

python week11/mutation_v2/scripts/make_chart.py \
  week7/mutation_v1_summary.json \
  week11/mutation_v2/mutation_v2_summary.json \
  week11/mutation_v2/v1_vs_v2.png

python week11/mutation_v2/scripts/build_excel.py
```
