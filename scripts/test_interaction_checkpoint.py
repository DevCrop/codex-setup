import copy
from pathlib import Path
import tempfile
import unittest

from interaction_checkpoint import record, resume, validate
from setup import read_json, save_json


class InteractionTests(unittest.TestCase):
    def sample(self):
        return {'task_id': 'qa-1', 'target_id': 'test-workspace',
                'stages': {'shell': {'status': 'failed', 'error_code': 'setup-refresh'},
                           'browser_connection': {'status': 'pass'}},
                'steps': [{'id': 'read', 'status': 'completed'},
                          {'id': 'submit', 'status': 'unknown-outcome'},
                          {'id': 'result', 'status': 'pending'},
                          {'id': 'layout', 'status': 'failed'}]}

    def test_independent_route_and_unknown_mutation_survive_resume(self):
        value = self.sample()
        result = resume(value)
        self.assertEqual(result['status'], 'observation-required')
        self.assertEqual(result['reconcile_first'], ['submit'])
        self.assertEqual(result['remaining'], ['result'])
        self.assertEqual(result['diagnose_first'], ['layout'])
        self.assertEqual(value['stages']['browser_connection']['status'], 'pass')
        self.assertNotIn('read', str(result))

    def test_exact_format_rejects_raw_data_and_duplicate_steps(self):
        for change in [{'url': 'https://private'}, {'task_id': '../path'},
                       {'stages': {'browser_connection': {'status': 'pass', 'raw_error': 'secret'}}},
                       {'steps': [{'id': 'same', 'status': 'pending'}] * 2}]:
            value = copy.deepcopy(self.sample())
            value.update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate(value)

    def test_accessibility_success_does_not_hide_screenshot_or_input_failure(self):
        value = self.sample()
        value['stages'].update({'native_accessibility': {'status': 'pass'},
                               'native_screenshot': {'status': 'failed', 'error_code': 'capture-timeout'},
                               'native_input': {'status': 'failed', 'error_code': 'geometry-unavailable'},
                               'browser_input': {'status': 'pass'}})
        validate(value)
        self.assertEqual(value['stages']['native_screenshot']['status'], 'failed')
        value['stages']['input'] = {'status': 'pass'}
        with self.assertRaises(ValueError):
            validate(value)

    def test_user_stop_cannot_resume_from_saved_passes(self):
        value = self.sample()
        value['stages']['user_control'] = {'status': 'stopped', 'error_code': 'human-stop'}
        self.assertEqual(resume(value)['status'], 'user-resume-required')
        value['stages']['browser_input'] = {'status': 'pass'}
        self.assertEqual(resume(value)['status'], 'user-resume-required')

    def test_replace_one_checkpoint_preserves_other_findings(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(ValueError):
                record(root, self.sample())
            save_json(root / 'routine-review.json', {'findings': {'pending': 1},
                      'feedback_loop': {'lessons': {'existing': {'status': 'pending'}}}})
            record(root, self.sample())
            second = self.sample()
            second['task_id'] = 'qa-2'
            record(root, second)
            actual = read_json(root / 'routine-review.json')
            self.assertEqual(actual['feedback_loop']['interaction_checkpoint']['task_id'], 'qa-2')
            self.assertEqual(actual['findings'], {'pending': 1})
            self.assertIn('existing', actual['feedback_loop']['lessons'])


if __name__ == '__main__':
    unittest.main()
