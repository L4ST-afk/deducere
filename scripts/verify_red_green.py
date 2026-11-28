#!/usr/bin/env python3
"""对鸟 Deducere · 雉闸——红绿双态证伪硬闸（verify_red_green.py）。

## 为什么有这个脚本

假回归最常见的形态：修复前根本没跑红过——pristine diff 下测试本来就过，
改完自然也过，于是「修复有效」无从谈起。本闸把「先复现红（非零退出码且
命中真实症状）、修复后跑绿（同一命令退出 0）」固化成命令级证据。

## 怎么判

- `--expect red`：命令必须返回非 0；给了 `--match` 正则时，stdout 或 stderr
  必须命中该症状正则，否则判「症状不匹配」，并**打印命令的实际末行**——锁红的人先读它，
  再决定是探针撞了别的闸还是 `--match` 写成了邻近失败；⛔ 不改 `--match` 去迁就输出。
  rc=0 判「假复现」。未给 `--match`
  时只确认非零退出，不核症状。`ImportError`／`NameError`／`AttributeError`／`SyntaxError`
  默认判「回路错误」而非症状红；错误类本身就是目标症状时，用 `--match` 精确命中该类可放行。
- `--expect green`：同一条命令必须返回 0；非 0 判「回归未通过」。
  ⛔ `--match` 仅限 red；green 携带 `--match` 按参数错误拒绝（rc=2）。

## 输入面

`--cmd` 是调用方授权的完整可信 shell 命令；⛔ 从报错症状文本拼接命令串。
本闸不解析命令里的管道／复合语句，也不保存跨调用状态：先红后绿的配对证明
归辨征／验真问的流程证据，本闸只判单次命令状态。

## 退出码

0 = 当前状态与期望一致（红灯已锁定 / 红灯已转绿）
1 = 状态与期望不符（假复现 / 症状不匹配 / 回归未过）
2 = 参数、正则或执行环境错误（跑不成 / 超时 / 未取得判定结果）

## 用法

    # 修复前锁死红灯（必须非 0 且命中症状）
    python3 scripts/verify_red_green.py --expect red --cmd "pytest tests/test_bug.py" --match "TimeoutError"

    # 修复后验证转绿（同一条命令必须返回 0）
    python3 scripts/verify_red_green.py --expect green --cmd "pytest tests/test_bug.py"
"""

import argparse
import re
import subprocess
import sys

COMMAND_TIMEOUT = 300
FIXTURE_ERROR_RE = re.compile(r"(?<![A-Za-z])(ImportError|NameError|AttributeError|SyntaxError)(?=:)")


def _usage(msg: str) -> int:
    print(f"[USAGE ERROR] {msg}", file=sys.stderr)
    return 2


def main() -> int:
    parser = argparse.ArgumentParser(description="对鸟 Deducere 红绿双态证伪硬闸")
    parser.add_argument("--expect", choices=["red", "green"], required=True,
                        help="期望状态：red 或 green")
    parser.add_argument("--cmd", required=True,
                        help="用于复现与验证的完整可信 shell 命令")
    parser.add_argument("--match", default="",
                        help="red 状态下输出必须命中的症状正则（仅限 red）")
    args = parser.parse_args()

    cmd = (args.cmd or "").strip()
    if not cmd:
        return _usage("--cmd 不能为空命令。")
    if args.expect == "green" and args.match:
        return _usage("--match 仅限 --expect red；green 模式不核症状正则。")

    symptom_re = None
    if args.match:
        try:
            symptom_re = re.compile(args.match)
        except re.error as exc:
            return _usage(f"症状正则非法: {exc}")

    try:
        proc = subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            errors="replace", timeout=COMMAND_TIMEOUT,
        )
    except OSError as exc:
        return _usage(f"命令启动失败: {exc}")
    except subprocess.TimeoutExpired:
        return _usage(f"命令超过 {COMMAND_TIMEOUT}s 未结束，未取得判定结果。")

    stdout = proc.stdout or ""
    stderr = proc.stderr or ""

    if args.expect == "red":
        if proc.returncode == 0:
            print("[FAIL] 假复现拦截：--expect red 状态下命令竟返回 0（未复现故障）。",
                  file=sys.stderr)
            return 1
        hit = None
        if symptom_re:
            hit = symptom_re.search(stdout) or symptom_re.search(stderr)
        fixture = FIXTURE_ERROR_RE.search((stdout or "") + "\n" + (stderr or ""))
        if fixture and (not hit or fixture.group(1) not in hit.group(0)):
            print(f"[FAIL] 回路错误拦截：输出出现 {fixture.group(1)}，先修测试夹具／符号／导入，"
                  "不得把它当用户症状的红。若该错误类本就是目标症状，请用 --match 精确命中它。",
                  file=sys.stderr)
            return 1
        if symptom_re:
            if not hit:
                # 实际末行一并给出（2026-11-28）：只说「未命中」，锁红的人得原样重跑翻长输出。
                # 当场三条红重锁三次，每次多花一个来回——读到的失败行其实早已在手里。
                last = next((ln.strip() for ln in reversed((stdout + "\n" + stderr).splitlines())
                             if ln.strip()), "")
                print(f"[FAIL] 症状不匹配：命令虽失败（rc={proc.returncode}），"
                      f"但输出未命中正则 /{args.match}/。实际末行：「{last[:160]}」"
                      "——先读它：多半是探针撞了别的闸，或 --match 写成了邻近失败（J2）；"
                      "⛔ 不改 --match 去迁就输出，回去修探针。", file=sys.stderr)
                return 1
            print(f"[PASS-RED] 故障已锁定（rc={proc.returncode}），症状证据有效。")
            return 0
        print(f"[PASS-RED] 命令非零退出（rc={proc.returncode}）；"
              f"未提供 --match，未核症状。")
        return 0

    if proc.returncode != 0:
        print(f"[FAIL] 回归未通过：--expect green 状态下命令仍失败（rc={proc.returncode}）。",
              file=sys.stderr)
        return 1
    print("[PASS-GREEN] 本次命令符合 green 期望（rc=0）；"
          "前序红灯与命令一致性由流程证据核验。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
