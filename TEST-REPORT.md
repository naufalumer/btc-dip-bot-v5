# TEST-REPORT — BTC dip-buy bot v5, make.fun btc-race-24h-20261118-1444

## Dev window

- 1,440 one-minute bars, 17 Nov 2026 14:44 UTC → 18 Nov 2026 14:44 UTC
  (the 24 hours ending at the opening), 0 gaps.
- BTC $65,083.31 → $63,260.75, **-2.80%**. Shape: sharp drop in hour 0–1
  ($65,083 → $63,724), flat ~$63,700 for hours 2–4, recovery to ~$64,950 by
  hour 8, flat ~$64,400–64,600 for hours 9–18, then a slide to $63,261 in
  the last hour.
- Buy-and-hold: **-$31.64** (float sim). Hold cash: $0.00.

## Grid search (float simulator, `dev/grid.py`)

1,932 variants across four families: A momentum, B mean-reversion (v4 rule),
C momentum + trailing stop, D mean-reversion + stop-loss. Only 156/1,932
profitable — this is a hard window for a long-only bot.

- Best momentum: +$2.94 (lb=60, enter +0.70%, TP +2.00%). Momentum is dead
  here: the window's rallies are snap-backs, not trends.
- v4 rule (60-bar / -1.00% dip / +1.60% TP / +1.20% rebound): **+$8.98**,
  but its third entry (bar 1435) is flattened at a loss at the window end.
- **Winner, family D: lb=60, dip -1.70%, TP +1.20%, stop -1.20%: +$16.37**
  (float), 2 round trips, MDD -1.12%.

## Plateau check (`dev/plateau.py`, `dev/plateau2.py`)

- Family B box (lb 20–60 / dip 120–180 / TP 80–160 / rebound 30–100):
  203/300 profitable, median +$2.61, max +$16.37.
- Family D box (lb 20–60 / dip 120–180 / TP 80–160 / stop 80–160):
  **252/300 profitable, median +$7.91, max +$16.37.** The stop-loss family
  is the more robust box, which is why it was chosen over plain
  mean-reversion.
- Sensitivity at lb=60, stop=120 (float PnL): dip 160–180 all give +$16.37
  at TP=120; dip 150–200 all positive at TP=120 (+$7.62 to +$16.37).
  The chosen dip=170 sits in the middle of the 160–180 plateau.
- Trailing exits HURT on this window (trail 40–80 bps: +$0.68 to -$3.48):
  the recoveries are choppy and a tight trail banks them too early. Not used.
- The rebound leg (v4's exit on 60-bar return > +X%) also hurts here: it
  fires on a "recovery vs an hour ago" that is still below the entry price
  (e.g. B lb=60 dip=150 TP=120 reb=50 sells bar 192 at -$4.28). Not used;
  exits are take-profit and stop-loss only.
- No-entry-in-last-30-bars guard: neutral on dev (no entries in the last
  120 bars for this rule) — kept as race-window protection, stated as such
  in main.py.

## Chosen rule (main.py)

- LOOKBACK=60, DIP_BPS=170, TAKE_PROFIT_BPS=120, STOP_BPS=120,
  NO_ENTRY_LAST_BARS=30, WINDOW_BARS=1440, MAX_SLIPPAGE_BPS=500.
- Float-sim trades: buy $63,736.76 (bar 66) → sell $64,273.66 (bar 86),
  +$7.62; buy $63,980.78 (bar 103) → sell $64,588.17 (bar 472), +$8.75.

## Exact-integer replay (dev gate, `dev/replay.py`, 2 runs)

Mirrors the kit harness's truncating integer fill math (fee 4 bps, modelled
slippage 2 bps, constant-product impact vs open depth). Feeds hello + 1,440
batches to the bot subprocess (`python3 -P -s main.py`, PYTHONHASHSEED=0).

- Run 1: PnL **+$16.37 (16,366,748 micro-USDC)**, 4 fills, MDD **-1.12%**,
  0 rejections.
- Run 2: identical — PnL +$16.37, 4 fills, MDD -1.12%, 0 rejections.
- Deterministic: action logs byte-identical, sha256
  `b0fb90d1f567cbcab9d140bb77e6dbdce59645e5574736ef3dc6e0b2432e2eb7`
  (both runs).
- Fills (price in $): buy 63,736.77710 → sell 64,273.60840;
  buy 63,980.79598 → sell 64,588.12928.
- **Dev gate: PASS** (net PnL > $0). Exact replay agrees with the float sim
  to the cent (+$16.37 both).

## Official-harness cross-check

- `grade-local --driver process` on the kit's momentum baseline:
  **-$23.87** (net_pnl_quote_units -23,865,251, 1 trade). The float sim
  reproduces the same trade (buy at bar 24, hold to end) at -$23.874 —
  agreement to $0.009. The fill math is validated against the official
  harness; no Docker on this VM, so the Python bot is proven by the
  exact-integer replay instead, same as v4.

## Honest caveat

Both dev-window round trips ride snap-back recoveries after a -1.7%
one-hour drop. If the race window drops -1.7% in an hour and keeps falling
instead of snapping back, the stop-loss caps that trip at about -1.20%
plus the ~26 bps round-trip cost — but repeated dip-buy-stop-out cycles
would still bleed. The mean-reversion bet is that this market keeps
snapping back, as it did all through the dev window.
