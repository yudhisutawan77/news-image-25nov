# THE WORLD — Wednesday 25 November 2026

[![make.fun](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/c/news-image-20261125)
![Rank](https://make.fun/badge/news-image-20261125/yudhisutawan77/news-image-25nov/rank.svg)
![Reward](https://make.fun/badge/news-image-20261125/yudhisutawan77/news-image-25nov/reward.svg)

A one-image front page summing up the world's news of **Wednesday 25 November 2026**,
drawn by `main.py` (pure Python standard library: a hand-built 5x7 bitmap font,
pixel-art illustrations and a hand-rolled PNG encoder — no packages, no network).

[make.fun](https://make.fun) — entry for the `news-image-20261125` competition.

## The day's stories in the picture

1. **Ukraine confirms drone hit on Russian ship** — Zelenskiy says Kyiv struck a
   Russian cargo ship in the Gulf of Finland; Norway, a firm ally, urges caution.
   (Reuters)
2. **Riyadh tower hit** — A Houthi strike hits Riyadh's tallest tower; 11 wounded,
   Saudi civil defence says. (Reuters)
3. **Medal for Giuliani** — Trump awards the Medal of Freedom to Rudy Giuliani at
   the White House. (Reuters)
4. **Huawei convicted** — A US jury convicts Huawei of trade-secret theft and bank
   fraud over its Iran business. (Reuters)
5. **Quake shakes Nepal** — A magnitude 5.6 earthquake hits Nepal near the Chinese
   border; tremors felt across eastern India. (Reuters / AP)

## Run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `out/entry.png` (1024x1024, under 1 MiB), deterministically — two runs
produce byte-identical output.
