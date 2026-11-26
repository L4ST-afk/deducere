#!/usr/bin/env python3
"""对鸟 Deducere · 双硬闸回归测试（test_deducere.py）。

验证 check_clean.py（收尾洁癖）与 verify_red_green.py（红绿证伪）
对残留探针、假复现、症状不匹配、回归未过具备真实拦截能力。

跑法：
    python3 -m unittest discover -s tests -q
    python3 tests/test_deducere.py

离线、零外部依赖；每条用例自建临时目录／临时 Git 仓。
"""

import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLEAN_SCRIPT = ROOT / "scripts" / "check_clean.py"
RG_SCRIPT = ROOT / "scripts" / "verify_red_green.py"


def git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo), "-c", "user.email=t@example.com",
         "-c", "user.name=test", *args],
        capture_output=True, text=True,
    )


def run_clean(repo: Path, *allow: str) -> subprocess.CompletedProcess:
    args = [sys.executable, str(CLEAN_SCRIPT), "--repo", str(repo)]
    for a in allow:
        args += ["--allow-file", a]
    return subprocess.run(args, capture_output=True, text=True)


def run_rg(expect: str, cmd: str, match: str = "") -> subprocess.CompletedProcess:
    args = [sys.executable, str(RG_SCRIPT), "--expect", expect, "--cmd", cmd]
    if match:
        args += ["--match", match]
    return subprocess.run(args, capture_output=True, text=True)


PY_EXIT0 = "exit 0"
PY_EXIT1_TIMEOUT = "echo TimeoutError: boom >&2; exit 1"
PY_EXIT1_OTHER = "echo OtherError: x >&2; exit 1"
PY_EXIT1_STDOUT = "echo TimeoutError: boom; exit 1"


class CleanGateFixture(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = Path(self._tmp.name) / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-q")
        self.write("main.py", "print('hello')\n")
        git(self.repo, "add", "main.py")
        git(self.repo, "commit", "-q", "-m", "baseline")
        head = git(self.repo, "rev-parse", "HEAD")
        self.assertEqual(head.returncode, 0, head.stderr)

    def write(self, name: str, text: str) -> Path:
        p = self.repo / name
        p.write_text(text, encoding="utf-8")
        return p


class TestCleanGate(CleanGateFixture):
    def test_01_clean_repo_passes(self):
        res = run_clean(self.repo)
        self.assertEqual(res.returncode, 0, msg=res.stderr)

    def test_02_tracked_marker_rejected_unstaged_and_staged(self):
        self.write("main.py", "print('hello')\n[DEBUG-a1] probe value=42\n")
        res = run_clean(self.repo)
        self.assertEqual(res.returncode, 1)
        self.assertIn("DEBUG-a1", res.stderr)
        # 即使 git add 进了暂存区，也必须同样拦截
        git(self.repo, "add", "main.py")
        res_staged = run_clean(self.repo)
        self.assertEqual(res_staged.returncode, 1)
        self.assertIn("DEBUG-a1", res_staged.stderr)

    def test_03_untracked_marker_rejected(self):
        self.write("proto.py", "[DEBUG-b2] scratch\n")
        res = run_clean(self.repo)
        self.assertEqual(res.returncode, 1)
        self.assertIn("proto.py", res.stderr)

    def test_04_allow_file_exempts_untracked(self):
        self.write("notes.md", "[DEBUG-c3] documented probe\n")
        res = run_clean(self.repo, "notes.md")
        self.assertEqual(res.returncode, 0, msg=res.stderr)

    def test_05_non_git_dir_rc2(self):
        with tempfile.TemporaryDirectory() as d:
            res = run_clean(Path(d))
            self.assertEqual(res.returncode, 2)

    def test_06_tracked_allow_file_exempts(self):
        self.write("main.py", "print('hello')\n[DEBUG-d4] probe\n")
        res = run_clean(self.repo, "main.py")
        self.assertEqual(res.returncode, 0, msg=res.stderr)
        git(self.repo, "add", "main.py")
        res_staged = run_clean(self.repo, "main.py")
        self.assertEqual(res_staged.returncode, 0, msg=res_staged.stderr)

    def test_07_deleted_line_marker_not_flagged(self):
        self.write("main.py", "print('hello')\n[DEBUG-old] committed baseline\n")
        git(self.repo, "add", "main.py")
        git(self.repo, "commit", "-q", "-m", "with marker")
        self.write("main.py", "print('hello')\n")
        res = run_clean(self.repo)
        self.assertEqual(res.returncode, 0, msg=res.stderr)

    def test_08_rename_does_not_flag(self):
        git(self.repo, "mv", "main.py", "app.py")
        res = run_clean(self.repo)
        self.assertEqual(res.returncode, 0, msg=res.stderr)

    def test_09_symlink_untracked_not_read(self):
        link = self.repo / "link_to_hosts"
        link.symlink_to("/etc/hosts")
        res = run_clean(self.repo)
        self.assertEqual(res.returncode, 2)
        self.assertIn("软链", res.stderr)

    def test_10_unreadable_file_rc2(self):
        if os.geteuid() == 0:
            self.skipTest("root 绕过 DAC 权限，用例不适用")
        f = self.write("proto.py", "[DEBUG-e5] scratch\n")
        os.chmod(f, 0o000)
        try:
            res = run_clean(self.repo)
            self.assertEqual(res.returncode, 2)
            self.assertIn("不可读", res.stderr)
        finally:
            os.chmod(f, stat.S_IRUSR | stat.S_IWUSR)

    def test_11_worktree_gitdir_file_not_rc2(self):
        wt = self.repo.parent / "wt"
        git(self.repo, "worktree", "add", str(wt))
        res = run_clean(wt)
        self.assertNotEqual(res.returncode, 2, msg=res.stderr)

    def test_12_binary_file_not_false_positive(self):
        blob = self.repo / "blob.dat"
        blob.write_bytes(b"\x00\x01\x02 print('x')\n")
        res = run_clean(self.repo)
        self.assertEqual(res.returncode, 0, msg=res.stderr)

    def test_13_chinese_filename_allow_exempt(self):
        self.write("探针.py", "[DEBUG-f6] scratch\n")
        res = run_clean(self.repo, "探针.py")
        self.assertEqual(res.returncode, 0, msg=res.stderr)


class TestRedGreenGate(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.side = Path(self._tmp.name) / "side.txt"

    def test_14_green_pass(self):
        res = run_rg("green", PY_EXIT0)
        self.assertEqual(res.returncode, 0, msg=res.stderr)
        self.assertIn("PASS-GREEN", res.stdout)

    def test_15_green_still_failing_rejected(self):
        res = run_rg("green", PY_EXIT1_OTHER)
        self.assertEqual(res.returncode, 1)
        self.assertIn("回归未通过", res.stderr)

    def test_16_red_with_symptom_stderr_pass(self):
        res = run_rg("red", PY_EXIT1_TIMEOUT, match="TimeoutError")
        self.assertEqual(res.returncode, 0, msg=res.stderr)
        self.assertIn("PASS-RED", res.stdout)

    def test_17_red_stdout_only_symptom_pass(self):
        res = run_rg("red", PY_EXIT1_STDOUT, match="TimeoutError")
        self.assertEqual(res.returncode, 0, msg=res.stderr)
        self.assertIn("PASS-RED", res.stdout)

    def test_18_red_but_command_passed_rejected(self):
        res = run_rg("red", PY_EXIT0)
        self.assertEqual(res.returncode, 1)
        self.assertIn("假复现", res.stderr)

    def test_19_red_symptom_mismatch_rejected(self):
        res = run_rg("red", PY_EXIT1_OTHER, match="TimeoutError")
        self.assertEqual(res.returncode, 1)
        self.assertIn("症状不匹配", res.stderr)

    def test_20_bad_regex_rc2(self):
        res = run_rg("red", PY_EXIT1_TIMEOUT, match="[unclosed")
        self.assertEqual(res.returncode, 2)

    def test_21_green_with_match_rejected_rc2(self):
        for match in ("TimeoutError", "[unclosed"):
            cmd = f"touch {self.side}; exit 0"
            res = run_rg("green", cmd, match=match)
            self.assertEqual(res.returncode, 2, msg=res.stderr)
            self.assertFalse(self.side.exists(), "参数错误时被测命令不应执行")

    def test_22_blank_cmd_rc2(self):
        res = run_rg("green", "   ")
        self.assertEqual(res.returncode, 2)

    def test_23_missing_cmd_rc2(self):
        res = subprocess.run(
            [sys.executable, str(RG_SCRIPT), "--expect", "green"],
            capture_output=True, text=True,
        )
        self.assertEqual(res.returncode, 2)

    def test_24_invalid_expect_rc2(self):
        res = run_rg("bogus", PY_EXIT0)
        self.assertEqual(res.returncode, 2)

    def test_25_fixture_errors_are_not_symptom_red(self):
        for error in ("ImportError", "NameError", "AttributeError", "SyntaxError"):
            with self.subTest(error=error):
                cmd = f"echo '{error}: broken fixture' >&2; exit 1"
                res = run_rg("red", cmd, match="ExpectedSymptom")
                self.assertEqual(res.returncode, 1)
                self.assertIn("回路错误", res.stderr)

    def test_26_fixture_error_without_match_is_rejected(self):
        res = run_rg("red", "echo 'AttributeError: wrong symbol' >&2; exit 1")
        self.assertEqual(res.returncode, 1)
        self.assertIn("回路错误", res.stderr)

    def test_27_fixture_error_as_explicit_target_passes(self):
        res = run_rg(
            "red", "echo 'AttributeError: intended symptom' >&2; exit 1",
            match="AttributeError",
        )
        self.assertEqual(res.returncode, 0, msg=res.stderr)
        self.assertIn("PASS-RED", res.stdout)


if __name__ == "__main__":
    unittest.main()
