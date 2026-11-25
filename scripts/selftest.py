#!/usr/bin/env python3
"""离线自检（冒烟级）：本 skill 的脚本「语法能过、文件在、被引用时能起来」。
⛔ 不联网、不读凭据、不写业务文件。

⚠️ 边界：这**不是判据级回归**——只证「脚本没坏到语法都过不去」；
业务口径（红绿双态、探针残留拦截）由 `tests/test_deducere.py` 的
unittest 套件承担，跑法：`python3 -m unittest discover -s tests -q`。
入口探测失败时打 SKIP 并写明原因，**不计入通过**（⛔ 不把「起不来」粉饰成绿）。
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ENTRY = ["check_clean.py", "verify_red_green.py"]


def main():
    ok = True
    for f in sorted(x for x in os.listdir(HERE) if x != "selftest.py"):
        p = os.path.join(HERE, f)
        try:
            if f.endswith(".py"):
                with open(p, encoding="utf-8") as fh:
                    compile(fh.read(), p, "exec")
            elif f.endswith((".js", ".mjs")):
                node = shutil.which("node")
                if not node:
                    print("SKIP node 不在 PATH，跳过 " + f)
                    continue
                r = subprocess.run([node, "--check", p], capture_output=True,
                                   text=True, timeout=30)
                if r.returncode != 0:
                    print("FAIL node --check " + f + ": " + (r.stderr or r.stdout)[-200:])
                    ok = False
            elif f.endswith(".sh"):
                r = subprocess.run(["bash", "-n", p], capture_output=True,
                                   text=True, timeout=30)
                if r.returncode != 0:
                    print("FAIL bash -n " + f + ": " + r.stderr[-200:])
                    ok = False
        except Exception as e:
            print("FAIL 检查 " + f + ": " + str(e))
            ok = False

    for ep_name in ENTRY:
        ep = os.path.join(HERE, ep_name)
        if not os.path.isfile(ep):
            print("SKIP 入口 " + ep_name + " 不存在（脚本可能已改名），本项不计入通过")
            continue
        try:
            r = subprocess.run([sys.executable, ep, "--help"], capture_output=True,
                               text=True, timeout=30)
            if r.returncode != 0:
                print("SKIP 入口 " + ep_name + " --help 起不来（rc=" + str(r.returncode) +
                      "，需参数或依赖），本项不计入通过")
        except Exception as e:
            print("SKIP 入口 " + ep_name + " 探测异常：" + str(e))

    print("PASS 冒烟自检（语法级）" if ok else "FAIL 冒烟自检（语法级）")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
