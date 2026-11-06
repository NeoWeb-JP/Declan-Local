"""Visible persona migration without changing existing registration or aliases."""
import json
from pathlib import Path
import unittest
import test_commands as fixtures
from jarvis_test import agent
from jarvis_test.followup import followup
from jarvis_test.information_dialogue import parse
from jarvis_test.satellite_stop import is_spoken_stop
from jarvis_test.social import social_reply
from jarvis_test.voice_text import spoken_text

ROOT=Path(__file__).resolve().parents[1]

class Branding(unittest.TestCase):
    def test_public_names_agree_and_domain_matches_package(self):
        folder=ROOT/'custom_components'/'declan_local'
        manifest=json.loads((folder/'manifest.json').read_text())
        strings=json.loads((folder/'strings.json').read_text())
        english=json.loads((folder/'translations'/'en.json').read_text())
        hacs=json.loads((ROOT/'hacs.json').read_text())
        self.assertEqual(manifest['name'],hacs['name'])
        self.assertEqual(strings['title'],manifest['name'])
        self.assertEqual(english,strings)
        self.assertEqual(manifest['domain'],'declan_local')
        self.assertEqual(agent.JarvisAgent._attr_name,'Declan')
        self.assertEqual(agent.JarvisAgent._attr_unique_id,'jarvis_local_test')

    def test_declan_and_legacy_aliases_work_without_hardware_claim(self):
        for name in ('Declan','Jarvis'):
            self.assertTrue(is_spoken_stop(name+', stop'))
            self.assertIsNotNone(social_reply('hello '+name,None,{}))
            self.assertIsNotNone(social_reply('thank you '+name,None,{}))
            self.assertEqual(followup(name+', make them dimmer'),('dim __previous_lights__',False))
            self.assertEqual(parse("what's the weather "+name)['topic'],'weather')

    def test_written_owner_name_and_entity_keys_are_not_pronunciation_migrations(self):
        written='Good morning, Edd. person.eddy stays unchanged.'
        self.assertEqual(spoken_text(written),'Good morning, Ed. person.eddy stays unchanged.')
        self.assertIn('Edd',written)
        self.assertEqual(spoken_text('Eddie / person.edd / edd_key'),'Eddie / person.edd / edd_key')

    def test_guest_catalogue_is_impersonal_and_home_bedtime_stays_downstairs(self):
        catalogue=json.loads((ROOT/'custom_components'/'declan_local'/'responses.json').read_text())
        self.assertEqual(set(catalogue),{'Home','Guest'})
        guest=' '.join(line for pool in catalogue['Guest'].values() for line in pool).lower()
        for private in ('jaco','edd','naturist','clothing','in bed'):
            self.assertNotIn(private,guest)
        for line in catalogue['Home']['bedtime']:
            self.assertIn('downstairs',line.lower())
            self.assertNotIn('upstairs',line.lower())
