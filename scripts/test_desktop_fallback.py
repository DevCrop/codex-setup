"""Routing safety and exact installed decision entrypoint; no external services."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

from agent_desktop import SOURCE

spec = importlib.util.spec_from_file_location('desktop_fallback', SOURCE / 'scripts/fallback.py')
fallback = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fallback)


def confirmed(**changes):
    result = dict(stage='connection', failure_origin='tool_runtime',
                  technical_cause='tool_transport_refused', cause_confirmed=True,
                  policy_state='allowed', permission_state='granted', human_stop=False,
                  runtime_stop=False, user_input_reserved=False,
                  target_kind='native', same_target_verified=True,
                  browser_url_verified=False, action_delivery='not_delivered',
                  switch_already_attempted=False)
    result.update(changes)
    return result


class FallbackTests(unittest.TestCase):
    def test_confirmed_causes_switch(self):
        for cause in fallback.CAUSES:
            with self.subTest(cause=cause):
                self.assertEqual(fallback.classify(confirmed(technical_cause=cause))['decision'], 'switch')

    def test_denials_uncertainty_and_wrong_failures_stop(self):
        cases = [dict(policy_state='denied'), dict(policy_state='unknown'),
                 dict(permission_state='denied'), dict(permission_state='unknown'),
                 dict(human_stop=True), dict(runtime_stop=True),
                 dict(stage='action'), dict(stage='observation'),
                 dict(failure_origin='website'), dict(cause_confirmed=False),
                 dict(technical_cause='timeout'), dict(technical_cause='policy_stop'),
                 dict(technical_cause='tool_missing'), dict(technical_cause='login_required'),
                 dict(action_delivery='unknown'), dict(action_delivery='delivered_unverified'),
                 dict(action_delivery='delivered_verified'), dict(same_target_verified=False),
                 dict(target_kind='other'), dict(switch_already_attempted=True)]
        for changes in cases:
            with self.subTest(changes=changes):
                self.assertEqual(fallback.classify(confirmed(**changes))['decision'], 'stop')

    def test_browser_requires_url_and_original_policy(self):
        self.assertEqual(fallback.classify(confirmed(target_kind='browser'))['reason'], 'browser_url_not_established')
        self.assertEqual(fallback.classify(confirmed(target_kind='browser', browser_url_verified=True))['decision'], 'switch')
        self.assertEqual(fallback.classify(confirmed(target_kind='browser', browser_url_verified=True,
                                                    runtime_stop=True))['decision'], 'stop')

    def test_stop_overrides_concurrent_connection_failure(self):
        self.assertEqual(fallback.classify(confirmed(runtime_stop=True))['reason'], 'human_or_runtime_stop')

    def test_gaming_blocks_even_confirmed_headless_candidate(self):
        self.assertEqual(fallback.classify(confirmed(user_input_reserved=True))['reason'], 'desktop_reserved_for_user')
        self.assertEqual(fallback.classify(confirmed(target_kind='browser', browser_url_verified=True,
                                                   user_input_reserved=True))['decision'], 'stop')

    def test_missing_fields_extra_fields_and_wrong_types_fail_closed(self):
        for key in confirmed():
            missing = confirmed()
            del missing[key]
            self.assertEqual(fallback.classify(missing)['decision'], 'stop')
        for evidence in [None, [], {}, confirmed(raw_message='private'), confirmed(human_stop='false'),
                         confirmed(same_target_verified=1), confirmed(cause_confirmed='true'),
                         confirmed(technical_cause=[]), confirmed(stage={})]:
            with self.subTest(evidence_type=type(evidence).__name__):
                self.assertEqual(fallback.classify(evidence)['decision'], 'stop')

    def test_cli_never_executes_desktop_and_returns_distinct_exit_codes(self):
        for evidence, expected in [(confirmed(), 0), (confirmed(runtime_stop=True), 2)]:
            proc = subprocess.run([sys.executable, '-B', str(SOURCE / 'scripts/fallback.py')],
                                  input=json.dumps(evidence), capture_output=True, text=True)
            self.assertEqual(proc.returncode, expected)
            self.assertEqual(json.loads(proc.stdout)['decision'], 'switch' if expected == 0 else 'stop')
        for raw in ['not json', 'x' * 8193]:
            proc = subprocess.run([sys.executable, '-B', str(SOURCE / 'scripts/fallback.py')],
                                  input=raw, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 2)


if __name__ == '__main__':
    unittest.main()
