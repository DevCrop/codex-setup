import unittest

from render_heartbeat import render


class HeartbeatTests(unittest.TestCase):
    def test_new_host_cannot_inherit_automatic_upgrade_authority(self):
        for record in ({}, {'maintenance_authorization': {'mode':'compatible-global-stable-tools',
                                                         'approved_on':'2026-10-05','automation_id':'other'}}):
            self.assertIn('Host authorization: Review-only',render(record))
        copied={'maintenance_authorization':{'mode':'compatible-global-stable-tools',
                'approved_on':'2026-10-05','automation_id':'trace','host_identity':'first-host'}}
        self.assertIn('Host authorization: Review-only',render(copied,host_identity='another-host'))

    def test_exact_local_authorization_keeps_scope_and_completion_checks(self):
        prompt=render({'maintenance_authorization': {'mode':'compatible-global-stable-tools',
                       'approved_on':'2026-10-05','automation_id':'trace','host_identity':'first-host'}},
                      host_identity='first-host')
        self.assertIn('Human-approved on 2026-10-05',prompt)
        self.assertIn('check_closure.py',prompt)
        self.assertIn('does not authorize future GitHub publication',prompt)
        self.assertNotIn('{{authorization}}',prompt)


if __name__ == '__main__':
    unittest.main()
