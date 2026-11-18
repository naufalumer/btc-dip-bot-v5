"""BTC dip-buy bot v5 for make.fun "Race a BTC trading bot live for 24 hours"
(competition btc-race-24h-20261118-1444).

Strategy (chosen by backtest on THIS competition's published dev window;
see TEST-REPORT.md): a 60-bar mean-reversion rule with a stop-loss. The dev
window trends DOWN -2.80% ($65,083 -> $63,261): buy-and-hold loses -$31.64
and the best momentum variant makes only +$2.94, while dip-buying the
sharp one-hour drops and banking the snap-back works — 252 of 300 variants
in the (lookback 20-60 / dip 120-180 / take-profit 80-160 / stop 80-160)
box are profitable, median +$7.91.
  - One asset (CBBTC), long only, at most one open position, full size (100%
    of cash, capped by hello caps max_weight_bps).
  - Keep the last 60 one-minute closes. Enter when the 60-bar return falls
    below -1.70% — a sharp one-hour drop, not a slow drift.
  - While long, exit on EITHER leg:
      (a) take-profit: the latest close is +1.20% above the signal close
          (the close at which the buy was decided). A fill-price variant
          of this leg was tried and REJECTED: pricing the take-profit off
          the fill instead of the signal close exits one trip later and
          misses the second entry entirely (+$10.45 on the replay vs
          +$16.37 — see TEST-REPORT.md), so the take-profit stays on the
          signal close.
      (b) stop-loss: the latest close is -1.20% below the ACTUAL FILL
          PRICE of the buy (captured from the batch's fills the bar after
          the order — the fill lands a bar later at the next open, so the
          loss is cut off what was actually paid; before the fill arrives
          the signal close stands in). The stop never fired on the dev
          window, so this change does not alter the dev result; it is
          accuracy for the leg that matters — the loss-cutting one.
    The stop never fired on the dev window (stop 80/120/160 bps all give the
    same +$16.37); it is insurance for the race window, where a down-trend
    could otherwise hold a dip-buy to a large flatten loss.
  - No new entries in the last 30 bars of the window (both windows are
    1,440 one-minute bars per the published rules): a buy that late has no
    time to reach the take-profit and would be flattened at whatever price
    the window ends at. This guard never fired on the dev window either —
    it is race-window protection, stated as such.
  - That is the whole rule. On the dev window it makes 2 round trips and
    finishes +$16.37 net of all fees (float simulator; exact-integer replay
    in TEST-REPORT.md): buy $63,736.76 -> sell $64,273.66 (+$7.62), then
    buy $63,980.78 -> sell $64,588.17 (+$8.75).
  - Deterministic: no clock, no randomness, no environment, no files. The
    decision is a pure function of the closes seen so far, the batch seq,
    and the signal close remembered at entry. The bot never trades on a
    warm-up batch (orders there are rejected anyway).
  - max_slippage_bps 500: a normal 1-minute move is a few bps, so a fill at
    the next open is far inside it; the cap only guards against a wild gap.

Honest caveat: both dev-window round trips ride snap-back recoveries after
a -1.7% one-hour drop. If the race window drops -1.7% in an hour and then
keeps falling instead of snapping back, the stop-loss caps that trip at
about -1.20% plus the ~26 bps round-trip cost — but a window of repeated
dip-buy-stop-out cycles would still bleed. The mean-reversion bet is that
this market keeps snapping back, as it did all through the dev window.

Wire protocol: agent-fun/bars-replay/v1, via the kit's Python shim, copied
byte-identical into vendor/makefun_bars.py (a kit SDK shim kept under vendor/
is left out of the authorship counts per RULES.txt).
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))

import makefun_bars

LOOKBACK = 60
DIP_BPS = 170          # enter when 60-bar return < -1.70%
TAKE_PROFIT_BPS = 120  # exit when close is +1.20% above the signal close
STOP_BPS = 120         # exit when close is -1.20% below the signal close
NO_ENTRY_LAST_BARS = 30  # no new entries in the last 30 bars of the window
WINDOW_BARS = 1440       # published window length (dev and race alike)
MAX_SLIPPAGE_BPS = 500

SYMBOL = "CBBTC"
_closes = []       # latest close per batch, as ints (price units)
_entry_close = None  # close of the bar on which the current buy was decided
_entry_fill = None   # actual fill price of the current buy (None until seen)


def _ret_bps(now, then):
    # (now / then - 1) in basis points, integer-exact.
    return (now - then) * 10000 // then


def on_batch(state, batch):
    global _entry_close, _entry_fill
    close = state.close(SYMBOL)
    if close is None:
        return []
    _closes.append(close)
    if state.warming_up:
        return []
    if len(_closes) <= LOOKBACK:
        return []
    ret = _ret_bps(close, _closes[-1 - LOOKBACK])
    held = state.positions.get(SYMBOL)
    # Capture the buy's actual fill price: fills arrive in the batch after
    # the order, and the position's qty matches the buy fill's qty. Until
    # it is seen, the signal close stands in as the reference price.
    if (held is not None and held.qty > 0 and _entry_close is not None
            and _entry_fill is None):
        for f in batch.get("fills") or []:
            if f.get("status") == "filled" and int(f.get("qty", "0")) == held.qty:
                _entry_fill = int(f["price"])
                break
    ref = _entry_fill if _entry_fill is not None else _entry_close
    if held is not None and held.qty > 0:
        # Take-profit first, off the signal close: bank the recovery before
        # it gives the gains back.
        if (_entry_close is not None
                and close * 10000 >= _entry_close * (10000 + TAKE_PROFIT_BPS)):
            _entry_close = None
            _entry_fill = None
            return [{"side": "sell", "symbol": SYMBOL, "qty": held.qty,
                     "max_slippage_bps": MAX_SLIPPAGE_BPS}]
        # Stop-loss, off the actual fill price: the drop was not a dip to
        # buy. Cut it.
        if (ref is not None
                and ref * 10000 >= close * (10000 + STOP_BPS)):
            _entry_close = None
            _entry_fill = None
            return [{"side": "sell", "symbol": SYMBOL, "qty": held.qty,
                     "max_slippage_bps": MAX_SLIPPAGE_BPS}]
        return []
    # Flat: a buy decided on a rejected/stale signal must not linger.
    _entry_close = None
    _entry_fill = None
    if state.seq >= WINDOW_BARS - NO_ENTRY_LAST_BARS:
        return []
    if ret < -DIP_BPS:
        room = state.weight_room(SYMBOL)
        spend = state.cash if state.cash < room else room
        if spend < int(state.hello["fees"]["min_notional_quote_units"]):
            return []
        _entry_close = close
        return [{"side": "buy", "symbol": SYMBOL,
                 "notional_quote_units": spend,
                 "max_slippage_bps": MAX_SLIPPAGE_BPS}]
    return []


makefun_bars.run(on_batch)
