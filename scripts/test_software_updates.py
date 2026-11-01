import json
from pathlib import Path
import platform
import subprocess
import tempfile
import unittest
from datetime import datetime,timezone

from setup import Deployment
from software_updates import allowed,refresh,skill_files,summarize


class SoftwareUpdateTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.home=self.root/'home';self.home.mkdir()
        (self.home/'config.toml').write_text('model="chosen"\n',encoding='utf-8')
        self.dep=Deployment(home=self.home,state=self.root/'state',personal_skills=self.root/'skills')
        self.key='fixture@openai-curated-remote'
        self.row={'pluginId':self.key,'name':'fixture','marketplaceName':'openai-curated-remote',
                  'version':'1','enabled':True,'authPolicy':'ON_USE','source':{'source':'remote'}}
        self.auth={'maintenance_authorization':{'software_updates':{'policy':'reviewed-existing-software-v1',
            'host_identity':platform.node(),'automation_id':'trace','approved_on':'2026-10-25','installed_plugin_ids':[self.key]}}}

    def tearDown(self):
        self.temp.cleanup()

    def test_authority_and_new_identity_are_not_inherited(self):
        self.assertFalse(allowed({}))
        self.assertFalse(allowed(self.auth,host='other'))
        self.auth['maintenance_authorization']['software_updates']['installed_plugin_ids']=[]
        def run(argv,**kw):
            self.assertNotIn('add',argv)
            return subprocess.CompletedProcess(argv,0,json.dumps({'installed':[self.row]}),'')
        result=refresh(self.dep,'cli',self.auth,[self.row],run=run)
        self.assertEqual(result['status'],'attention')
        self.assertEqual(result['outcomes'][0]['status'],'new-identity-needs-review')

    def test_only_skill_files_are_fingerprinted(self):
        root=self.root/'metadata';root.mkdir();(root/'SKILL.md').write_text('fixture')
        (root/'auth.json').write_text('DO_NOT_READ')
        result=skill_files(root)
        self.assertEqual(len(result),1)
        self.assertNotIn('DO_NOT_READ',json.dumps(result))

    def test_native_owner_update_verified_then_cached_without_reinstall(self):
        package=self.home/'plugins/cache/openai-curated-remote/fixture/2';(package/'.codex-plugin').mkdir(parents=True)
        (package/'.codex-plugin/plugin.json').write_text('{"version":"2"}')
        calls=[];after={**self.row,'version':'2'}
        def run(argv,**kw):
            calls.append(argv)
            payload={'pluginId':self.key,'version':'2','installedPath':str(package),'authPolicy':'ON_USE'} if 'add' in argv else {'installed':[after]}
            return subprocess.CompletedProcess(argv,0,json.dumps(payload),'')
        result=refresh(self.dep,'cli',self.auth,[self.row],run=run)
        self.assertEqual(result['outcomes'][0]['status'],'owner-verified')
        self.assertTrue(result['outcomes'][0]['changed'])
        self.assertEqual((self.home/'config.toml').read_text(),'model="chosen"\n')
        routine={**self.auth,'software_updates':result};calls.clear()
        cached=refresh(self.dep,'cli',routine,[after],run=run)
        self.assertEqual(cached['outcomes'][0]['status'],'reused-current-owner-check')
        self.assertEqual(cached['last_owner_refresh'],result['last_owner_refresh'])
        self.assertTrue(all('add' not in c for c in calls))

    def test_disabled_plugins_and_local_sources_are_preserved(self):
        rows=[{**self.row,'enabled':False}]
        def run(argv,**kw):
            self.assertNotIn('add',argv)
            return subprocess.CompletedProcess(argv,0,json.dumps({'installed':rows}),'')
        result=refresh(self.dep,'cli',self.auth,rows,run=run)
        self.assertEqual(result['outcomes'][0]['status'],'disabled-preserved')

    def test_owner_failure_stops_and_does_not_claim_success(self):
        def run(argv,**kw):
            return subprocess.CompletedProcess(argv,1,'','sensitive error') if 'add' in argv else subprocess.CompletedProcess(argv,0,json.dumps({'installed':[self.row]}),'')
        result=refresh(self.dep,'cli',self.auth,[self.row],run=run)
        self.assertEqual(result['status'],'attention')
        self.assertEqual(result['owner_checks'],{})
        self.assertNotIn('sensitive error',json.dumps(result))


if __name__=='__main__':unittest.main()
