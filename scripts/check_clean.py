#!/usr/bin/env python3
"""对鸟 Deducere · 鸽闸——收尾洁癖硬闸（check_clean.py）。

## 为什么有这个脚本

调试件最容易腐化的两处：残留 `[DEBUG-<id>]` 探针日志、未清理的临时原型。
纸面上写「收尾清干净」不等于工作区真的清干净；本脚本把可机械判定的部分
（探针标记残留）变成退出码，在净痕问汇报完成前物理阻断。

## 查什么（只读，零外部依赖）

扫描范围（⛔ 不是全仓历史扫描）：
1. 已跟踪文件的暂存区＋工作区**新增行**里是否含 `[DEBUG-<id>]` 标记；
2. 未被 `.gitignore` 忽略的未跟踪新文件全文里是否含同款标记；
3. `--allow-file` 列出的路径豁免（仓内相对文件路径，全等匹配）。

不在本闸范围：基线提交里已存在的标记、被忽略路径、二进制／UTF-16 文件、
临时原型与临时脚本——后者按 `references/reporting-and-handoff.md` §二
清理清单人工核对。

## 退出码

0 = 扫描范围内无探针残留，且所有目标文件均可读可确认
1 = 发现残留调试脏物（逐条打印文件与命中标记）
2 = 环境异常或扫描未完成（非 Git 仓库、git 查询失败、目标不可读等跑不成的情况）

## 用法

    python3 scripts/check_clean.py --repo .
    python3 scripts/check_clean.py --repo . --allow-file docs/debug-notes.md
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

DEBUG_MARKER_RE = re.compile(r"\[DEBUG-[A-Za-z0-9_-]+\]")

# 阻断可能把扫描指向另一个仓库的环境变量；外部 diff/textconv 配置一并隔离
_BLOCKED_ENV = {
    "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE",
    "GIT_EXTERNAL_DIFF", "GIT_DIFF_OPTS", "GIT_ATTR_NOSYSTEM",
}

GIT_ESCAPES = {"n": 10, "t": 9, '"': 34, "\\": 92,
               "a": 7, "b": 8, "f": 12, "r": 13, "v": 11}


class GateScanError(Exception):
    """git 查询或目标文件读取失败；本次扫描未完成，不能判洁净。"""


def _unquote_git_path(raw: str) -> str:
    """还原 Git 对含引号、反斜杠或控制字符路径做的 C 风格转义。"""
    raw = raw.rstrip("\t")
    if len(raw) < 2 or raw[0] != '"' or raw[-1] != '"':
        return raw
    body = raw[1:-1]
    out = bytearray()
    i = 0
    while i < len(body):
        ch = body[i]
        if ch == "\\" and i + 1 < len(body):
            octal = body[i + 1:i + 4]
            if len(octal) == 3 and all(c in "01234567" for c in octal):
                out.append(int(octal, 8) & 0xFF)
                i += 4
                continue
            code = GIT_ESCAPES.get(body[i + 1])
            if code is not None:
                out.append(code)
                i += 2
                continue
        out.extend(ch.encode("utf-8"))
        i += 1
    return out.decode("utf-8", errors="replace")


def run_git(repo: Path, args: list[str]) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k not in _BLOCKED_ENV}
    res = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True, errors="replace", env=env,
    )
    if res.returncode != 0:
        raise GateScanError(
            (res.stderr or res.stdout or f"git {' '.join(args)} rc={res.returncode}").strip()
        )
    return res


def _markers_in(text: str) -> set[str]:
    return {m.group(0) for m in DEBUG_MARKER_RE.finditer(text)}


def scan_tracked(repo: Path, allow_set: set[str]) -> list[str]:
    hits: list[str] = []
    diff_base = ["-c", "core.quotepath=false", "diff", "--no-color",
                 "--no-ext-diff", "--unified=0"]
    for diff_cmd in (diff_base, [*diff_base, "--cached"]):
        res = run_git(repo, diff_cmd)
        current_file = None
        for line in res.stdout.splitlines():
            if line.startswith("+++ b/"):
                current_file = _unquote_git_path(line[6:].strip())
            elif line.startswith("+++ /dev/null"):
                current_file = None
            elif line.startswith("+") and not line.startswith("+++"):
                if current_file and current_file not in allow_set:
                    markers = _markers_in(line)
                    if markers:
                        hits.append(
                            f"{current_file}: 残留探针标记 {', '.join(sorted(markers))}"
                        )
    return hits


def scan_untracked(repo: Path, allow_set: set[str]) -> tuple[list[str], list[str]]:
    hits: list[str] = []
    problems: list[str] = []
    res = run_git(repo, ["ls-files", "--others", "--exclude-standard", "-z"])
    for rel in res.stdout.split("\0"):
        rel = _unquote_git_path(rel.strip())
        if not rel or rel in allow_set:
            continue
        p = repo / rel
        if p.is_symlink():
            problems.append(f"{rel}（未跟踪软链）: 未解引用，未纳入扫描")
            continue
        if not p.is_file():
            problems.append(f"{rel}: 无法确认是普通文件，未纳入扫描")
            continue
        try:
            raw = p.read_bytes()
        except OSError as exc:
            problems.append(f"{rel}: 不可读（{exc}），未纳入扫描")
            continue
        texts = [raw.decode("utf-8", "ignore"), raw.decode("utf-16", "ignore")]
        markers = {m for t in texts for m in _markers_in(t)}
        if markers:
            hits.append(
                f"{rel}（未跟踪文件）: 残留探针标记 {', '.join(sorted(markers))}"
            )
    return hits, problems


def main() -> int:
    parser = argparse.ArgumentParser(description="对鸟 Deducere 收尾洁癖硬闸")
    parser.add_argument("--repo", default=".", help="目标 Git 仓库路径（仓库根）")
    parser.add_argument("--allow-file", action="append", default=[],
                        help="豁免路径（仓内相对文件路径，全等匹配，可重复）")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    if not (repo / ".git").exists():
        print(f"[USAGE ERROR] 非 Git 仓库根目录: {repo}", file=sys.stderr)
        return 2

    allow_set: set[str] = set()
    for raw in args.allow_file:
        p = Path(raw)
        if raw.startswith("/") or p.is_absolute() or ".." in p.parts:
            print(f"[USAGE ERROR] --allow-file 只接受仓内相对路径: {raw}", file=sys.stderr)
            return 2
        allow_set.add(p.as_posix())

    try:
        top = run_git(repo, ["rev-parse", "--show-toplevel"]).stdout.strip()
        if Path(top).resolve() != repo:
            raise GateScanError(f"目标目录 {repo} 不属于仓库根 {top}")
        tracked_hits = scan_tracked(repo, allow_set)
        untracked_hits, problems = scan_untracked(repo, allow_set)
    except GateScanError as exc:
        print(f"[USAGE ERROR] 扫描未完成: {exc}", file=sys.stderr)
        return 2

    if problems:
        print("[FAIL] 以下目标未纳入扫描，不能判洁净：", file=sys.stderr)
        for prob in sorted(set(problems)):
            print(f"  - {prob}", file=sys.stderr)
        return 2

    dirty_hits = [*tracked_hits, *untracked_hits]
    if dirty_hits:
        print("[FAIL] 收尾洁癖硬闸拦截——检测到未清理的调试探针：", file=sys.stderr)
        for hit in sorted(set(dirty_hits)):
            print(f"  - {hit}", file=sys.stderr)
        return 1

    print("[PASS] 收尾洁癖校验通过：扫描范围内无残留 [DEBUG-*] 探针。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
