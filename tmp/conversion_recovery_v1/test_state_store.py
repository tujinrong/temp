import json
import tempfile
import unittest
from pathlib import Path
from state_store import save_stage, validate_stage, acknowledge_readback, safe_path

class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name); self.run=self.root/'checkpoint'; self.source=self.root/'source.md'
        self.source.write_text('確認済み本文\n',encoding='utf-8'); self.deps={'input':'source-hash','rules':'rules-hash','py':'code-hash'}
        self.m=save_stage(self.run,'body',self.deps,{'candidate/body.md':self.source})
    def test_complete_stage_reuses(self):
        self.assertEqual(validate_stage(self.run,self.m,self.deps)['action'],'REUSE')
    def test_missing_artifact_reruns_only_stage(self):
        record=json.loads(self.m.read_text()); safe_path(self.run,record['snapshot']+'/candidate/body.md').unlink()
        self.assertEqual(validate_stage(self.run,self.m,self.deps)['action'],'RERUN_STAGE')
    def test_tampering_is_rejected(self):
        record=json.loads(self.m.read_text()); safe_path(self.run,record['snapshot']+'/candidate/body.md').write_text('changed')
        self.assertEqual(validate_stage(self.run,self.m,self.deps)['action'],'RERUN_STAGE')
    def test_changed_dependencies_rerun(self):
        for key in self.deps:
            with self.subTest(key=key):
                changed=dict(self.deps);changed[key]='new';self.assertEqual(validate_stage(self.run,self.m,changed)['action'],'RERUN_STAGE')
    def test_incomplete_write_keeps_previous_manifest(self):
        old=self.m.read_bytes()
        with self.assertRaises(FileNotFoundError):save_stage(self.run,'body',self.deps,{'missing':self.root/'absent'})
        self.assertEqual(self.m.read_bytes(),old)
    def test_same_artifact_is_idempotent(self):
        old=self.m.read_bytes();save_stage(self.run,'body',self.deps,{'candidate/body.md':self.source});self.assertEqual(old,self.m.read_bytes())
    def test_path_escape_rejected(self):
        with self.assertRaises(ValueError):save_stage(self.run,'body',self.deps,{'../../escape':self.source})
    def test_local_save_not_remote_success(self):
        self.assertEqual(validate_stage(self.run,self.m,self.deps)['durability'],'LOCAL_ONLY')
        with self.assertRaises(ValueError):acknowledge_readback(self.run,self.m,self.deps,'a'*40,{})
    def test_wrong_remote_payload_rejected(self):
        with self.assertRaises(ValueError):acknowledge_readback(self.run,self.m,self.deps,'a'*40,{'candidate/body.md':b'wrong'})
    def test_exact_readback_receipt(self):
        r=acknowledge_readback(self.run,self.m,self.deps,'a'*40,{'candidate/body.md':self.source.read_bytes()})
        self.assertEqual(r['status'],'READBACK_VERIFIED')

if __name__=='__main__':unittest.main()
