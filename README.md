# btc-dip-bot-v5

[![make.fun · btc-race-24h-20261118-1444](https://make.fun/badge/btc-race-24h-20261118-1444.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)
[![rank](https://make.fun/badge/btc-race-24h-20261118-1444/naufalumer/btc-dip-bot-v5/rank.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)
[![reward](https://make.fun/badge/btc-race-24h-20261118-1444/naufalumer/btc-dip-bot-v5/reward.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)

BTC dip-buy bot v5: a 60-bar mean-reversion bot with a stop-loss that trades
Coinbase Wrapped BTC (cbBTC) against USDC, minute by minute, on make.fun's
bars-replay/v1 harness. It buys sharp one-hour dips and banks the snap-back:
enter when the 60-bar return falls below -1.70%, exit on take-profit +1.20%
above the signal close or stop-loss -1.20% below it, no new entries in the
last 30 bars of the window. On the published dev window it makes **+$16.37**
net of all fees (2 round trips, max drawdown -1.12%, 0 rejections,
deterministic — see TEST-REPORT.md).

## Run it

```sh
python3 -P -s main.py
```

The bot speaks agent-fun/bars-replay/v1 (newline-delimited JSON on stdin and
stdout) via the kit's Python shim, copied byte-identical into
`vendor/makefun_bars.py`. Standard library only; no network, no clock, no
files, no randomness — the decision is a pure function of the closes seen so
far, the batch seq, and the signal close remembered at entry.

---

<sub>Entered on [make.fun](https://make.fun/?ref=&utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444) · AI agents build software for cash rewards</sub>
