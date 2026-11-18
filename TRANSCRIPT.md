# TRANSCRIPT — BTC dip-buy bot v5, make.fun btc-race-24h-20261118-1444

Build session record (this run, 18 Nov 2026, ~21:50–22:30 WIB).

## What happened

1. Read the v4 entry's PARENT-HANDOFF.md + STATUS.md + SUBMISSION.txt
   (previous round, same race format) and the new competition's requirements
   JSON (already fetched: ~/workspace/make-fun/btc-race-24h-20261118-1444-
   requirements.json, 115 KB).
2. Downloaded the new kit: GET /api/competitions/btc-race-24h-20261118-1444/kit
   (manifest, HTTP 200) then GET /c/btc-race-24h-20261118-1444/kit (tarball,
   7,519,918 bytes, bundle_sha256 157048c6db4067eb660ddfcf63962509d87f4463cee
   7b29b60cf9bd93bf2c934 matches manifest). Kit supports --parent-session
   (bundle --help lists it). Dev window 17–18 Nov, 1,440 bars, 0 gaps.
3. Ran a fresh grid search on the new dev window (dev/grid.py, 1,932
   variants, 4 families): only 156 profitable. Momentum best +$2.94; v4
   rule +$8.98; mean-reversion + stop-loss wins. Plateau check
   (dev/plateau.py, dev/plateau2.py): D box 252/300 profitable, median
   +$7.91. Chose lb=60 / dip -170 bps / TP +120 bps / stop -120 bps /
   no-entry-last-30-bars.
4. Created GitHub repo naufalumer/btc-dip-bot-v5 with the gh CLI (logged in
   as naufalumer; repo created 2026-11-18T15:00:38Z, after opening
   14:44:00Z). Ran kit init in the repo in the FOREGROUND: LICENSE (MIT) +
   drand anchor `makefun anchor 2c8ddbc2d49339f3a2813d271af212dfd155b285
   round 34070235` (round_min 34069892) — the anchor line is in this
   session's tool results before the first write of main.py.
5. Wrote main.py fresh in this session (new file, mean-reversion +
   stop-loss rule), copying the new kit's sdk/makefun_bars.py byte-identical
   into vendor/ (sha256 80452b00... matches the kit manifest).
6. Wrote dev/grid.py, dev/plateau.py, dev/plateau2.py (float simulator +
   grid searches, this session) and dev/replay.py (exact-integer replay,
   this session, adapted from v4's replay). Replay (2 runs): +$16.37,
   16,366,748 micro-USDC, 4 fills, MDD -1.12%, 0 rejections, action logs
   byte-identical (sha256 b0fb90d1...).
7. Cross-checked with the official grader: grade-local --driver process on
   the kit's momentum baseline, -$23.87 — reproduced by the float simulator
   to $0.009 (see TEST-REPORT.md). Process driver runs node only; no
   Docker on this VM, so the Python bot is proven by the exact-integer
   replay instead.
8. Wrote README.md (badges from the requirements readme_template),
   TEST-REPORT.md and this file; committed and pushed to
   https://github.com/naufalumer/btc-dip-bot-v5 (commit ac74fcc); set the
   repo About via gh (description, homepage,
   topics makefun/ai-agents/bounties/trading).
9. Bundle + check are the parent's step (muse-usage rows are written only
   once this builder run completes): see PARENT-HANDOFF.md. A bundle
   (without usage rows) and a local check were run in this session against
   the final commit: 15 passed, 1 failed (thinking_priced — 0 usage rows,
   fixed by the parent in PARENT-HANDOFF.md §1–§2), 4 skipped, 3 checked at
   submission. thinking_revised passes (main.py final content from 4
   messages); thinking_fresh passes (all 201 credited lines show the
   anchor before their first counted write — the foreground kit init
   worked). Bundle 236,514 bytes, sha256
   41487cc3ba2ac953e8c8121c787c66bd40c79d2024e97ee32e47a50931e26b63; the
   parent MUST re-bundle with usage rows before submitting. A fill-price
   revision of the exit legs was tried and partly rejected on the replay
   (+$10.45 vs +$16.37 — see TEST-REPORT.md, Revision note).
