"""Real filesystem upgrade/refusal checks on platforms with a POSIX shell."""
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'custom_components'/'jarvis_voice_bridge'

class InstallerHashes(unittest.TestCase):
    def test_current_checksum_manifest_matches_actual_package(self):
        script=(ROOT/'install-ha-bridge.sh').read_text()
        current=script.split("verify_current() {",1)[1].split("EOF",2)[1]
        rows=re.findall(r'([a-f0-9]{64})  ([a-z_.]+)',current)
        self.assertEqual(len(rows),7)
        for expected,name in rows:
            self.assertEqual(sha256((SOURCE/name).read_bytes()).hexdigest(),expected,name)

@unittest.skipUnless(shutil.which('sh') and shutil.which('sha256sum'),'POSIX installer checks run in Linux CI')
class InstallerUpgrade(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.target=self.root/'custom_components'/'jarvis_voice_bridge';self.target.mkdir(parents=True)
        fixture=json.loads((ROOT/'tests'/'fixtures'/'bridge-0.2.0.json').read_text())
        for name,text in fixture.items():(self.target/name).write_text(text,encoding='utf-8',newline='\n')

    def run_installer(self):
        return subprocess.run(['sh',str(ROOT/'install-ha-bridge.sh'),str(self.root)],capture_output=True,text=True)

    def test_upgrade_keeps_backup_and_second_run_is_noop(self):
        old=(self.target/'manifest.json').read_bytes()
        result=self.run_installer();self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual((self.target/'manifest.json').read_bytes(),(SOURCE/'manifest.json').read_bytes())
        backups=list((self.root/'jarvis_voice_bridge_backups').iterdir())
        self.assertEqual(len(backups),1)
        self.assertEqual((backups[0]/'manifest.json').read_bytes(),old)
        result=self.run_installer();self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('already installed',result.stdout)
        self.assertEqual(len(list((self.root/'jarvis_voice_bridge_backups').iterdir())),1)

    def test_local_edit_is_refused_without_mutation(self):
        path=self.target/'config_flow.py'
        path.write_text(path.read_text()+'\n# local edit\n')
        before=path.read_bytes()
        result=self.run_installer();self.assertNotEqual(result.returncode,0)
        self.assertEqual(path.read_bytes(),before)
        self.assertFalse((self.root/'jarvis_voice_bridge_backups').exists())
