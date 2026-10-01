import json
from pathlib import Path
import tempfile
import unittest
from src.checkpoint import save, verify, restore, cleanup, fingerprints, safe_name, save_files

class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory(); self.root = Path(self.t.name)
        self.cache = self.root/'checkpoint'; self.deps = {'input':'i','rules':'r','code':'c'}
        save(self.cache, 'candidate-01', self.deps, {'output/仕様.md':'# はじめに\n'.encode()}, next_action='independent evaluation')
    def tearDown(self): self.t.cleanup()
    def test_restore(self):
        restore(self.cache,self.root/'restored',self.deps)
        self.assertEqual((self.root/'restored/output/仕様.md').read_text(),'# はじめに\n')
    def test_idempotent(self):
        restore(self.cache,self.root/'restored',self.deps); restore(self.cache,self.root/'restored',self.deps)
    def test_changed_source(self):
        with self.assertRaises(ValueError): verify(self.cache,{**self.deps,'input':'changed'})
    def test_corrupt_archive(self):
        p=self.cache/'artifacts.zip';p.write_bytes(p.read_bytes()+b'bad')
        with self.assertRaises(ValueError): verify(self.cache,self.deps)
    def test_immutable(self):
        with self.assertRaises(FileExistsError): save(self.cache,'again',self.deps,{'a.md':b'x'},next_action='check')
    def test_paths(self):
        for name in ['../x','/tmp/x','a\\b','a/../x','']:
            with self.assertRaises(ValueError): safe_name(name)
    def test_different_target(self):
        d=self.root/'dest';(d/'output').mkdir(parents=True);(d/'output/仕様.md').write_text('newer')
        with self.assertRaises(FileExistsError): restore(self.cache,d,self.deps)
    def test_cleanup_guard(self):
        with self.assertRaises(ValueError): cleanup(self.cache,{}, {'verified':False})
        self.assertTrue((self.cache/'state.json').exists())
    def test_verified_cleanup(self):
        p=self.root/'final.md';p.write_text('final');files={'output/final.md':p}
        cleanup(self.cache,files,{'branch':'main','verified':True,'commit':'checked','files':fingerprints(files)})
        self.assertFalse((self.cache/'state.json').exists())
    def test_rule_or_code_invalidation(self):
        for key in ('rules','code'):
            with self.assertRaises(ValueError): verify(self.cache,{**self.deps,key:'changed'})
    def test_receipt_mismatch(self):
        p=self.root/'final.md';p.write_text('final')
        with self.assertRaises(ValueError): cleanup(self.cache,{'output/final.md':p},{'branch':'main','verified':True,'commit':'checked','files':{'output/final.md':'bad'}})
    def test_symlink_guard(self):
        d=self.root/'dest';d.mkdir();(d/'output').symlink_to(self.root/'outside')
        with self.assertRaises(ValueError): restore(self.cache,d,self.deps)

class PlainFileTests(unittest.TestCase):
    def test_restore_and_tamper(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); deps={'input':'x','rules':'r','code':'c'}
            save_files(root/'cp','step',deps,{'part.md':b'# Specification'},next_action='evaluate')
            restore(root/'cp',root/'out',deps)
            self.assertEqual((root/'out/part.md').read_bytes(),b'# Specification')
            (root/'cp/part.md').write_text('changed')
            with self.assertRaises(ValueError): verify(root/'cp',deps)
    def test_cleanup_does_not_remove_unlisted_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); deps={'input':'x'}; final=root/'final.md';final.write_text('done')
            save_files(root/'cp','step',deps,{'part.md':b'part'},next_action='evaluate')
            (root/'cp/unrelated.txt').write_text('keep')
            files={'output/spec.md':final}
            cleanup(root/'cp',files,{'branch':'main','verified':True,'commit':'real-verified','files':fingerprints(files)})
            self.assertTrue((root/'cp/unrelated.txt').exists())
            self.assertFalse((root/'cp/part.md').exists())
    def test_reserved_state(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(FileExistsError):
                save_files(Path(temp),'step',{'i':'x'},{'state.json':b'bad'},next_action='later')

if __name__=='__main__': unittest.main()
