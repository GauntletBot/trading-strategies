#!/usr/bin/env python3
"""
analyze_trades.py — rigorous checks on a TradingView Strategy Tester "List of Trades" export.
Version 1. tools/analyze_trades.py is always the latest version; earlier versions
are kept in tools/archive/analyze_trades_vN.py.

TradingView tells you what happened. This tells you whether it is likely to be real:
  * core stats from the trade list (equity-based, not % of position)
  * bootstrap confidence intervals for expectancy and profit factor
  * Monte Carlo on trade order (drawdown you should actually expect)
  * Deflated Sharpe Ratio — penalises you for how many variants you tried
  * year-by-year stability, and IS vs OOS comparison (walk-forward efficiency)
  * an experiment log so the trial count is never "forgotten"

Usage
  python analyze_trades.py trades.csv --capital 10000
  python analyze_trades.py oos.csv --compare is.csv --capital 10000
  python analyze_trades.py is.csv --log experiments.csv --label "donchian 20, htf D/50" --window IS
  python analyze_trades.py trades.csv --out report.md

Export: Strategy Tester -> "List of Trades" tab -> Download (CSV). XLSX also accepted.
Requires: pandas, numpy   (pip install pandas numpy openpyxl)
"""
from __future__ import annotations

import argparse
import math
import os
import sys
from datetime import datetime
from statistics import NormalDist

import numpy as np
import pandas as pd

N = NormalDist()
EULER_GAMMA = 0.5772156649


# ───────────────────────────── parsing ─────────────────────────────
def _find(cols, *must, exclude=()):
    for c in cols:
        lc = c.lower()
        if all(m in lc for m in must) and not any(e in lc for e in exclude):
            return c
    return None


def load_trades(path: str) -> pd.DataFrame:
    """Return one row per closed trade: entry_time, exit_time, pnl, side."""
    df = pd.read_excel(path) if path.lower().endswith((".xlsx", ".xls")) else pd.read_csv(path)
    df.columns = [str(c).strip() for c in df.columns]
    cols = list(df.columns)

    c_id = _find(cols, "trade") or cols[0]
    c_type = _find(cols, "type")
    c_date = _find(cols, "date")
    # Net P&L in currency (newer exports) or Profit in currency (older exports)
    c_pnl = (_find(cols, "net p&l", exclude=("%", "cumulative"))
             or _find(cols, "p&l", exclude=("%", "cumulative"))
             or _find(cols, "profit", exclude=("%", "cumulative")))
    if not all([c_type, c_date, c_pnl]):
        sys.exit(f"Could not recognise columns in {path}: {cols}")

    df[c_date] = pd.to_datetime(df[c_date], errors="coerce")
    df[c_pnl] = pd.to_numeric(df[c_pnl].astype(str).str.replace(r"[^\d.\-eE]", "", regex=True), errors="coerce")

    is_exit = df[c_type].astype(str).str.lower().str.startswith("exit")
    is_entry = df[c_type].astype(str).str.lower().str.startswith("entry")
    ex = df[is_exit].set_index(c_id)
    en = df[is_entry].set_index(c_id)
    # Drop open trades (TradingView labels them "Open" on the exit row / no exit row)
    ex = ex[ex["Signal"].astype(str).str.lower() != "open"] if "Signal" in ex.columns else ex

    out = pd.DataFrame({
        "exit_time": ex[c_date],
        "pnl": ex[c_pnl],
        "side": ex[c_type].astype(str).str.lower().str.replace("exit", "").str.strip(),
    })
    out["entry_time"] = en[c_date].reindex(out.index)
    out = out.dropna(subset=["pnl", "exit_time"]).sort_values("exit_time").reset_index(drop=True)
    if out.empty:
        sys.exit(f"No closed trades found in {path}")
    return out


# ───────────────────────────── metrics ─────────────────────────────
def equity_returns(pnl: np.ndarray, capital: float) -> tuple[np.ndarray, np.ndarray]:
    equity = capital + np.cumsum(pnl)
    before = np.concatenate([[capital], equity[:-1]])
    return pnl / before, equity


def max_dd_pct(equity: np.ndarray, capital: float) -> float:
    curve = np.concatenate([[capital], equity])
    peak = np.maximum.accumulate(curve)
    return float(((curve - peak) / peak).min() * -100)


def profit_factor(pnl: np.ndarray) -> float:
    gl = -pnl[pnl < 0].sum()
    return float(pnl[pnl > 0].sum() / gl) if gl > 0 else float("inf")


def core_stats(t: pd.DataFrame, capital: float) -> dict:
    pnl = t["pnl"].to_numpy()
    r, eq = equity_returns(pnl, capital)
    n = len(pnl)
    years = max((t["exit_time"].iloc[-1] - (t["entry_time"].iloc[0] if pd.notna(t["entry_time"].iloc[0]) else t["exit_time"].iloc[0])).days / 365.25, 1e-9)
    total = eq[-1] / capital - 1
    sd = r.std(ddof=1) if n > 1 else float("nan")
    sr = r.mean() / sd if sd and sd > 0 else float("nan")
    tpy = n / years
    skew = float(pd.Series(r).skew()) if n > 2 else 0.0
    kurt = float(pd.Series(r).kurt() + 3) if n > 3 else 3.0  # raw (non-excess) kurtosis
    tstat = sr * math.sqrt(n) if not math.isnan(sr) else float("nan")
    return dict(
        trades=n, years=years, trades_per_year=tpy,
        win_rate=float((pnl > 0).mean() * 100),
        profit_factor=profit_factor(pnl),
        expectancy=float(pnl.mean()),
        avg_win=float(pnl[pnl > 0].mean()) if (pnl > 0).any() else 0.0,
        avg_loss=float(pnl[pnl < 0].mean()) if (pnl < 0).any() else 0.0,
        total_return_pct=total * 100,
        cagr_pct=((1 + total) ** (1 / years) - 1) * 100 if total > -1 else -100.0,
        max_dd_pct=max_dd_pct(eq, capital),
        sharpe_trade=sr, sharpe_ann=sr * math.sqrt(tpy) if not math.isnan(sr) else float("nan"),
        skew=skew, kurt=kurt, tstat=tstat,
        p_value=1 - N.cdf(tstat) if not math.isnan(tstat) else float("nan"),
        _r=r,
    )


def bootstrap(pnl: np.ndarray, capital: float, iters: int, rng) -> dict:
    n = len(pnl)
    idx = rng.integers(0, n, size=(iters, n))
    samples = pnl[idx]
    means = samples.mean(axis=1)
    gp = np.where(samples > 0, samples, 0).sum(axis=1)
    gl = -np.where(samples < 0, samples, 0).sum(axis=1)
    pfs = np.divide(gp, gl, out=np.full(iters, np.inf), where=gl > 0)
    final = capital + samples.sum(axis=1)
    return dict(
        exp_ci=np.percentile(means, [5, 95]),
        pf_ci=np.percentile(pfs[np.isfinite(pfs)], [5, 95]) if np.isfinite(pfs).any() else [np.inf, np.inf],
        p_mean_le_0=float((means <= 0).mean()),
        p_loss=float((final < capital).mean()),
    )


def monte_carlo_dd(pnl: np.ndarray, capital: float, iters: int, rng) -> np.ndarray:
    dds = np.empty(iters)
    for i in range(iters):
        eq = capital + np.cumsum(rng.permutation(pnl))
        dds[i] = max_dd_pct(eq, capital)
    return dds


def deflated_sharpe(sr: float, n: int, skew: float, kurt: float, trials: int, sr_var: float | None) -> tuple[float, float]:
    """Bailey & Lopez de Prado (2014). Works on per-trade (non-annualised) Sharpe."""
    if trials < 1 or n < 3 or math.isnan(sr):
        return float("nan"), float("nan")
    v = sr_var if sr_var and sr_var > 0 else 1.0 / n
    if trials == 1:
        sr0 = 0.0
    else:
        sr0 = math.sqrt(v) * ((1 - EULER_GAMMA) * N.inv_cdf(1 - 1 / trials)
                              + EULER_GAMMA * N.inv_cdf(1 - 1 / (trials * math.e)))
    denom = math.sqrt(max(1 - skew * sr + (kurt - 1) / 4 * sr ** 2, 1e-12))
    return sr0, N.cdf((sr - sr0) * math.sqrt(n - 1) / denom)


def yearly(t: pd.DataFrame) -> pd.DataFrame:
    g = t.groupby(t["exit_time"].dt.year)["pnl"]
    return pd.DataFrame({"trades": g.size(), "pnl": g.sum().round(2), "win%": (g.apply(lambda s: (s > 0).mean() * 100)).round(1)})


# ───────────────────────────── report ─────────────────────────────
def fmt(x, d=2):
    if isinstance(x, float) and (math.isinf(x) or math.isnan(x)):
        return "∞" if x == float("inf") else "n/a"
    return f"{x:,.{d}f}"


def build_report(path, s, b, dds, sr0, dsr, trials, yr, cmp_s, dd_limit) -> tuple[str, list]:
    L = [f"# Backtest analysis — {os.path.basename(path)}", ""]
    L += ["## Core", "| metric | value |", "|---|---|"]
    rows = [("Closed trades", s["trades"], 0), ("Span (years)", s["years"], 1), ("Trades / year", s["trades_per_year"], 1),
            ("Win rate %", s["win_rate"], 1), ("Profit factor", s["profit_factor"], 2), ("Expectancy / trade", s["expectancy"], 2),
            ("Avg win / avg loss", f'{fmt(s["avg_win"])} / {fmt(s["avg_loss"])}', None),
            ("Total return %", s["total_return_pct"], 1), ("CAGR %", s["cagr_pct"], 1), ("Max drawdown % (actual order)", s["max_dd_pct"], 1),
            ("Sharpe (per trade / annualised)", f'{fmt(s["sharpe_trade"], 3)} / {fmt(s["sharpe_ann"])}', None),
            ("t-stat / one-sided p", f'{fmt(s["tstat"])} / {fmt(s["p_value"], 4)}', None)]
    for name, v, d in rows:
        L.append(f"| {name} | {v if d is None else fmt(float(v), d)} |")

    L += ["", "## Is the edge real?", "| test | result |", "|---|---|",
          f"| Expectancy 90% CI (bootstrap) | {fmt(b['exp_ci'][0])} … {fmt(b['exp_ci'][1])} |",
          f"| Profit factor 90% CI | {fmt(float(b['pf_ci'][0]))} … {fmt(float(b['pf_ci'][1]))} |",
          f"| P(true expectancy ≤ 0) | {fmt(b['p_mean_le_0'] * 100, 1)}% |",
          f"| Trials counted | {trials} |",
          f"| Sharpe hurdle from trials (per trade) | {fmt(sr0, 3)} |",
          f"| Deflated Sharpe Ratio | {fmt(dsr, 3)} (want > 0.95) |"]

    L += ["", "## Monte Carlo drawdown (trade order reshuffled)", "| percentile | max DD % |", "|---|---|"]
    for p in (50, 90, 95, 99):
        L.append(f"| {p}th | {fmt(float(np.percentile(dds, p)), 1)} |")
    L.append(f"\nP(max DD > {dd_limit:g}%) = {fmt(float((dds > dd_limit).mean() * 100), 1)}%")

    L += ["", "## By year", yr.to_markdown() if hasattr(yr, "to_markdown") else yr.to_string()]

    if cmp_s:
        wfe = s["cagr_pct"] / cmp_s["cagr_pct"] if cmp_s["cagr_pct"] not in (0,) else float("nan")
        L += ["", "## This file vs comparison (treat this file as OOS, comparison as IS)", "| metric | IS | OOS |", "|---|---|---|"]
        for k in ("trades", "win_rate", "profit_factor", "cagr_pct", "max_dd_pct", "sharpe_ann"):
            L.append(f"| {k} | {fmt(float(cmp_s[k]))} | {fmt(float(s[k]))} |")
        L.append(f"\nWalk-forward efficiency (OOS CAGR / IS CAGR) = {fmt(wfe)}  (≥ 0.5 is respectable; < 0 means the edge vanished)")

    # verdict
    checks = [
        (s["trades"] >= 100, f"≥100 trades (have {s['trades']}; <30 is anecdote)"),
        (s["p_value"] < 0.05, "expectancy significant at 5%"),
        (float(b["pf_ci"][0]) > 1.0, "PF 90% CI lower bound > 1"),
        (not math.isnan(dsr) and dsr > 0.95, "Deflated Sharpe > 0.95 given trials"),
        (float(np.percentile(dds, 95)) < dd_limit, f"95th pct MC drawdown < {dd_limit:g}%"),
        ((yr["pnl"] > 0).mean() >= 0.6, "≥60% of years profitable"),
    ]
    if cmp_s:
        checks.append((s["cagr_pct"] > 0 and cmp_s["cagr_pct"] > 0 and s["cagr_pct"] / cmp_s["cagr_pct"] >= 0.5, "OOS keeps ≥50% of IS CAGR"))
    L += ["", "## Verdict checklist"] + [f"- [{'x' if ok else ' '}] {txt}" for ok, txt in checks]
    passed = sum(ok for ok, _ in checks)
    L.append(f"\n**{passed}/{len(checks)} passed.** " + ("Candidate for forward (paper) testing." if passed == len(checks)
             else "Not yet deployable — see unchecked items."))
    return "\n".join(L), checks


def append_log(log_path, label, window, path, s, dsr, trials):
    row = dict(timestamp=datetime.now().isoformat(timespec="seconds"), label=label, window=window, file=os.path.basename(path),
               trades=s["trades"], win_rate=round(s["win_rate"], 2), profit_factor=round(s["profit_factor"], 3),
               cagr_pct=round(s["cagr_pct"], 2), max_dd_pct=round(s["max_dd_pct"], 2),
               sharpe_trade=round(s["sharpe_trade"], 4), sharpe_ann=round(s["sharpe_ann"], 3),
               p_value=round(s["p_value"], 5), dsr=round(dsr, 4) if not math.isnan(dsr) else "", trials_at_time=trials)
    pd.DataFrame([row]).to_csv(log_path, mode="a", header=not os.path.exists(log_path), index=False)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("trades")
    ap.add_argument("--capital", type=float, default=10000)
    ap.add_argument("--compare", help="in-sample trade list; main file is treated as out-of-sample")
    ap.add_argument("--trials", type=int, help="variants tried so far (default: rows in --log, else 1)")
    ap.add_argument("--log", help="experiment log CSV to read trial count from and append this run to")
    ap.add_argument("--label", default="", help="short description of params for the log")
    ap.add_argument("--window", default="", help="IS / OOS / WF-k etc. for the log")
    ap.add_argument("--dd-limit", type=float, default=25, help="max drawdown %% you could live with")
    ap.add_argument("--iters", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out", help="write markdown report here")
    a = ap.parse_args()

    rng = np.random.default_rng(a.seed)
    t = load_trades(a.trades)
    s = core_stats(t, a.capital)
    pnl = t["pnl"].to_numpy()

    sr_var, trials = None, a.trials
    if a.log and os.path.exists(a.log):
        lg = pd.read_csv(a.log)
        is_rows = lg[lg["window"].astype(str).str.upper().str.startswith(("IS", "WF"))] if "window" in lg else lg
        if trials is None:
            prior = max(len(is_rows), int(pd.to_numeric(is_rows.get("trials_at_time"), errors="coerce").max() or 0) if len(is_rows) else 0)
            this_is_trial = a.window.upper().startswith(("IS", "WF")) or not a.window
            trials = prior + (1 if this_is_trial else 0)  # OOS checks don't add a trial
        if len(is_rows) >= 2:
            sr_var = float(is_rows["sharpe_trade"].var(ddof=1))
    trials = trials or 1

    b = bootstrap(pnl, a.capital, a.iters, rng)
    dds = monte_carlo_dd(pnl, a.capital, min(a.iters, 3000), rng)
    sr0, dsr = deflated_sharpe(s["sharpe_trade"], s["trades"], s["skew"], s["kurt"], trials, sr_var)
    cmp_s = core_stats(load_trades(a.compare), a.capital) if a.compare else None

    report, _ = build_report(a.trades, s, b, dds, sr0, dsr, trials, yearly(t), cmp_s, a.dd_limit)
    print(report)
    if a.out:
        with open(a.out, "w") as f:
            f.write(report + "\n")
    if a.log:
        append_log(a.log, a.label, a.window, a.trades, s, dsr, trials)


if __name__ == "__main__":
    main()
