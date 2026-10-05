import unittest

from check_closure import evaluate


class ClosureTests(unittest.TestCase):
    def review(self, installed=None, release=None, registrations=None, routine=None):
        return evaluate({'version': '1.2.1'}, {'tools': {'rtk': {'version': '0.51.0'}}},
                        installed if installed is not None else {'version': '1.2.1'},
                        {'rtk': {'version': '0.51.0'}},
                        release if release is not None else {'status': 'collected', 'tagName': 'v1.2.1'},
                        registrations or {}, routine or {})

    def test_release_lag_is_not_successful_publication(self):
        findings = self.review(release={'status': 'collected', 'tagName': 'v1.1.4'})
        self.assertEqual(set(findings), {'publication-version'})

    def test_unavailable_github_and_missing_install_remain_unknown(self):
        findings = self.review(installed={}, release={'status': 'unknown', 'reason': 'offline'})
        self.assertIn('deployment-version', findings)
        self.assertEqual(findings['publication-unknown']['status'], 'unknown')

    def test_unchanged_baseline_needs_initial_review_only_for_registered_projects(self):
        findings = self.review(registrations={'projects': {'one': {}}},
                               routine={'projects': {'one': {'content_fingerprint': 'same'}, 'unregistered': {}}})
        self.assertEqual(set(findings), {'project-initial-review:one'})

    def test_reviewed_registered_project_and_matching_release_have_no_findings(self):
        self.assertEqual(self.review(registrations={'projects': {'one': {}}},
                                    routine={'projects': {'one': {'last_substantive_review': 'time'}}}), {})


if __name__ == '__main__':
    unittest.main()
