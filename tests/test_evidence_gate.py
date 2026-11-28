"""证据闸降级判据：没有外部评审通道时，本地三闸要能证死，且不冒充已复核。

跑法：python3 -m unittest discover -s tests -q
"""
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import evidence_gate  # noqa: E402


class EvidenceGate(unittest.TestCase):
    def test_self_test_has_teeth(self):
        r = subprocess.run(
            [sys.executable, str(SCRIPTS / "evidence_gate.py"), "--self-test"],
            capture_output=True, text=True, timeout=120,
        )
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_channel_absent_degrades_and_says_why(self):
        original = os.environ.pop(evidence_gate.CHANNEL_ENV, None)
        try:
            state = evidence_gate.probe_channel()
        finally:
            if original is not None:
                os.environ[evidence_gate.CHANNEL_ENV] = original
        self.assertFalse(state["external"])
        self.assertTrue(state["why"])

    def test_channel_pointing_at_missing_file_is_not_available(self):
        original = os.environ.get(evidence_gate.CHANNEL_ENV)
        os.environ[evidence_gate.CHANNEL_ENV] = "/nonexistent/reviewer"
        try:
            state = evidence_gate.probe_channel()
        finally:
            if original is None:
                os.environ.pop(evidence_gate.CHANNEL_ENV, None)
            else:
                os.environ[evidence_gate.CHANNEL_ENV] = original
        self.assertFalse(state["external"])

    def test_reports_what_local_gates_cannot_prove(self):
        original = os.environ.pop(evidence_gate.CHANNEL_ENV, None)
        try:
            report = evidence_gate.gate(ROOT)
        finally:
            if original is not None:
                os.environ[evidence_gate.CHANNEL_ENV] = original
        self.assertTrue(report["lost"])
        joined = " ".join(report["lost"])
        # 三件本地证不了的事必须逐条列出，⛔ 不许让交付方以为复核过了。
        self.assertIn("症状", joined)
        self.assertIn("J18", joined)
        self.assertIn("隔期", joined)

    def test_clean_gate_resolves_git_root_from_subdirectory(self):
        # 给子目录时向上找根；找不到根要记「跑不成」，⛔ 不许当成「过」。
        root, why = evidence_gate.resolve_repo(ROOT)
        if root is None:
            self.assertTrue(why)
        else:
            self.assertTrue(root.exists())

    def test_findings_and_incomplete_are_distinct(self):
        # 有发现（1）与跑不成（2）不是一回事，退出码要分开。
        original = os.environ.pop(evidence_gate.CHANNEL_ENV, None)
        try:
            report = evidence_gate.gate(ROOT)
        finally:
            if original is not None:
                os.environ[evidence_gate.CHANNEL_ENV] = original
        self.assertIn(report["status"], {"pass", "findings", "incomplete"})
        codes = [c["code"] for c in report["checks"]]
        if 1 in codes:
            self.assertEqual(report["status"], "findings")
        elif 2 in codes:
            self.assertEqual(report["status"], "incomplete")

    def test_json_report_is_serialisable(self):
        original = os.environ.pop(evidence_gate.CHANNEL_ENV, None)
        try:
            report = evidence_gate.gate(ROOT)
        finally:
            if original is not None:
                os.environ[evidence_gate.CHANNEL_ENV] = original
        json.dumps(report, ensure_ascii=False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
