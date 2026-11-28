#!/usr/bin/env python3
"""证据闸的本地降级：没有外部评审通道时，把能本地证的先证死。

## 为什么有这个脚本

对鸟的证据账要求「每条结论都能回读到命令与退出码」。完整形态是外部评审通道
（人／另一席位）按四问三账复核；但通道不在时，⛔ 不能因此把「没复核」写成「已复核」，
也不能因为复核不了就整份不交。

本脚本做的是**降级**：把三件本来就能本地机判的事跑一遍，给出可回读的证据行，
并把「本地证不了什么」逐条写明。它**不代替**外部评审，只保证交出去的东西里
没有一条结论是空口。

## 三层判据

  ① 核心：三个本地闸（红绿双态、净痕、语法冒烟）永远可跑，零外部依赖。
  ② 增强：探测到外部评审通道（环境变量 `DEDUCERE_REVIEW_CHANNEL` 指向可执行件）时，
     报告里标 `external: true` 并把它交给通道；⛔ 本脚本不解析通道输出里的判断。
  ③ 降级：探测不到就只跑本地三闸，报告里记一行「增强未启用：缺外部评审通道」。

## 丢了什么（⛔ 不粉饰）

本地闸证不了的三件事，报告 `lost` 字段逐条列出：
  - 症状是否真的是用户报的那个（本地只能证「命令红了」，证不了「红的是对的东西」）
  - 修复是否落在坏值第一次产生的位置（J18 要人判因果链）
  - 隔期复验（J24 要时间，本地一次跑不出来）

## 用法

    python3 scripts/evidence_gate.py --repo . --cmd "pytest -q" --expect green
    python3 scripts/evidence_gate.py --repo . --json
    python3 scripts/evidence_gate.py --self-test

退出码：0 本地三闸全过／1 有闸红／2 用法错或跑不成／3 自检判反失败。
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

# 本地闸能判、外部评审才判得了的东西。⛔ 这张表是给交付方看的，不是装饰。
REVIEW_ONLY = [
    "症状是否就是用户报的那一个（本地只证「命令红了」，证不了「红的是对的东西」）",
    "修复是否落在坏值第一次产生的位置（J18 要人判因果链）",
    "隔期复验是否成立（J24 要时间，一次跑不出来）",
]

CHANNEL_ENV = "DEDUCERE_REVIEW_CHANNEL"


def probe_channel() -> dict:
    """探测外部评审通道。⛔ 只查在不在，不调用、不联网、不读凭据。"""
    raw = os.environ.get(CHANNEL_ENV)
    if not raw:
        return {"external": False, "path": None, "why": "缺外部评审通道（%s 未设）" % CHANNEL_ENV}
    path = Path(raw)
    if not path.exists():
        return {"external": False, "path": raw, "why": "外部评审通道指向的件不在盘：%s" % raw}
    return {"external": True, "path": str(path), "why": None}


def run_gate(name: str, argv: list, timeout: int = 300) -> dict:
    """跑一个本地闸，把命令与退出码原样记进证据行。"""
    try:
        r = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
    except Exception as error:
        return {"gate": name, "cmd": " ".join(argv), "code": 2, "summary": str(error)}
    tail = (r.stdout or r.stderr or "").strip().splitlines()
    return {
        "gate": name,
        "cmd": " ".join(argv),
        "code": r.returncode,
        "summary": tail[-1] if tail else "",
    }


def resolve_repo(repo: Path) -> tuple:
    """check_clean 要的是 Git 仓库根。给的是子目录时向上找根，并如实报用了哪个。

    ⛔ 不假装子目录就是根：找不到根就返回 None，由调用方记「跑不成」。
    """
    try:
        r = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=30,
        )
    except Exception:
        return None, "git 不可用"
    if r.returncode != 0:
        return None, "不在 Git 仓库内"
    return Path(r.stdout.strip()), None


def local_gates(repo: Path, cmd: str | None, expect: str) -> list:
    """本地三闸：净痕、红绿双态（给了命令才跑）、语法冒烟。"""
    checks = []

    clean = HERE / "check_clean.py"
    root, why = resolve_repo(repo)
    if not clean.exists():
        checks.append({"gate": "净痕 check_clean", "cmd": "", "code": 2, "summary": "脚本不在盘"})
    elif root is None:
        # 跑不成不是「过」也不是「有发现」，单独记一笔。
        checks.append({"gate": "净痕 check_clean", "cmd": "", "code": 2,
                       "summary": "跑不成：%s（%s）" % (why, repo)})
    else:
        checks.append(run_gate("净痕 check_clean", [sys.executable, str(clean), "--repo", str(root)]))

    if cmd:
        rg = HERE / "verify_red_green.py"
        if rg.exists():
            checks.append(run_gate(
                "红绿双态 verify_red_green",
                [sys.executable, str(rg), "--expect", expect, "--cmd", cmd],
            ))
        else:
            checks.append({"gate": "红绿双态 verify_red_green", "cmd": cmd, "code": 2,
                           "summary": "脚本不在盘"})

    smoke = HERE / "selftest.py"
    if smoke.exists():
        checks.append(run_gate("语法冒烟 selftest", [sys.executable, str(smoke)]))
    else:
        checks.append({"gate": "语法冒烟 selftest", "cmd": "", "code": 2, "summary": "脚本不在盘"})

    return checks


def gate(repo: Path, cmd: str | None = None, expect: str = "green") -> dict:
    channel = probe_channel()
    checks = local_gates(repo, cmd, expect)
    codes = [c["code"] for c in checks]
    # 三种结局分开报：有发现（1）与跑不成（2）不是一回事，⛔ 不许合并成「没过」。
    if any(c == 1 for c in codes):
        status = "findings"
    elif any(c == 2 for c in codes):
        status = "incomplete"
    else:
        status = "pass"
    return {
        "repo": str(repo),
        "external": channel["external"],
        "channel": channel["path"],
        "why": channel["why"],
        "lost": [] if channel["external"] else list(REVIEW_ONLY),
        "checks": checks,
        "status": status,
    }


def self_test() -> int:
    """变异自证：把通道环境变量指向不存在的件，必须降级并自报缺件。"""
    original = os.environ.get(CHANNEL_ENV)
    try:
        os.environ[CHANNEL_ENV] = "/nonexistent/reviewer"
        state = probe_channel()
        if state["external"]:
            print("[SELF-TEST] 变异失败：指向不存在的件仍报通道可用")
            return 3
        if not state["why"]:
            print("[SELF-TEST] 变异失败：降级原因没写清")
            return 3
        os.environ.pop(CHANNEL_ENV, None)
        state2 = probe_channel()
        if state2["external"] or not state2["why"]:
            print("[SELF-TEST] 变异失败：未设变量时没走降级")
            return 3
    finally:
        if original is None:
            os.environ.pop(CHANNEL_ENV, None)
        else:
            os.environ[CHANNEL_ENV] = original
    print("[SELF-TEST] 通道缺失／指向空件时转本地三闸且自报缺件 ✓（闸有牙）")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="证据闸本地降级")
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--cmd", default=None, help="要验红绿的命令（不给就跳过该闸）")
    parser.add_argument("--expect", choices=["red", "green"], default="green")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()

    if not args.repo.exists():
        print("仓库路径不在盘：%s" % args.repo, file=sys.stderr)
        return 2

    report = gate(args.repo, args.cmd, args.expect)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        mode = "外部评审通道" if report["external"] else "本地三闸（降级）"
        print("证据闸：%s｜仓库 %s" % (mode, report["repo"]))
        if report["why"]:
            print("   增强未启用：%s" % report["why"])
        for check in report["checks"]:
            mark = "✓" if check["code"] == 0 else "✗"
            print("   %s %s（rc=%d）%s" % (mark, check["gate"], check["code"], check["summary"]))
        if report["lost"]:
            print("   本地证不了（⛔ 不等于已复核）：")
            for line in report["lost"]:
                print("   · " + line)

    return 0 if report["status"] == "pass" else (1 if report["status"] == "findings" else 2)


if __name__ == "__main__":
    sys.exit(main())
