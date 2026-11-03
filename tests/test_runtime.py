"""Hardware-independent regression tests for Kuhl's settings and generated bar."""
import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import desktop
import render


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='kuhl-runtime-')
        self.root = Path(self.tmp.name)
        self.data = self.root/'share/kuhl'
        self.state = self.root/'state/kuhl'
        self.config = self.root/'config'
        (self.data/'templates').mkdir(parents=True)
        (self.data/'themes.json').write_bytes((ROOT/'config/themes.json').read_bytes())
        self.patcher=patch.multiple(desktop, DATA=self.data, STATE=self.state,
                                    CONFIG=self.config, PREF_PATH=self.state/'preferences.json')
        self.patcher.start()
        self.render_patcher=patch.multiple(render, DATA=self.data, STATE=self.state,
                                          CONFIG=self.config, MANIFEST=self.state/'managed.json')
        self.render_patcher.start()

    def tearDown(self):
        self.render_patcher.stop();self.patcher.stop();self.tmp.cleanup()

    def test_bar_default_scaled_and_toggles(self):
        theme=json.loads((self.data/'themes.json').read_text())['frontier']
        conf,css=desktop.bar_files('frontier',theme)
        obj=json.loads(conf)
        self.assertEqual(obj['height'],34)
        self.assertEqual(obj['layer'],'top')
        self.assertIn('custom/close',obj['modules-right'])
        self.assertIn('niri msg action close-window',obj['custom/close']['on-click'])
        p=desktop.preferences()
        p['bar_scale']=1.50
        p['bar_position']='bottom'
        p['bar_modules']['close']=False
        desktop.save_preferences(p)
        conf,css=desktop.bar_files('frontier',theme)
        obj=json.loads(conf)
        self.assertEqual(obj['height'],51)
        self.assertEqual(obj['position'],'bottom')
        self.assertNotIn('custom/close',obj['modules-right'])
        self.assertIn('font-size: 20px',css.decode())

    def test_output_scale_and_user_edit_protection(self):
        path=self.config/'niri/output.kdl'
        with patch.object(desktop.shutil,'which',return_value=None):
            desktop.set_output('HDMI-A-1',1.25)
            self.assertIn('output "HDMI-A-1"',path.read_text())
            self.assertIn('scale 1.25',path.read_text())
            desktop.set_output('DP-1',1.5)
            self.assertIn('scale 1.5',path.read_text())
            before=path.read_text()
            with self.assertRaises(SystemExit):
                desktop.scale_value('500',0.75,3.0)
            self.assertEqual(path.read_text(),before)
            path.write_text('// custom manual edits\n')
            with self.assertRaises(SystemExit):
                desktop.set_output('DP-1',1.75)
            self.assertEqual(path.read_text(),'// custom manual edits\n')

    def test_gtk_restore_respects_manual_changes(self):
        values={'color-scheme':"'prefer-light'",'gtk-theme':"'Adwaita'",
                'icon-theme':"'Adwaita'",'text-scaling-factor':'1.0'}
        original=copy.copy(values)
        def fake(action,key,value=None):
            if action=='get':return values[key]
            values[key]=value
            return ''
        with patch.object(desktop,'gtk_call',side_effect=fake):
            desktop.sync_gtk('frontier')
            self.assertEqual(values['color-scheme'],"'prefer-dark'")
            self.assertEqual(values['icon-theme'],"'Papirus-Dark'")
            # If manually changed, Kuhl must not overwrite the user's newer choice.
            values['icon-theme']="'CustomIconTheme'"
            desktop.restore_gtk()
        self.assertEqual(values['color-scheme'],original['color-scheme'])
        self.assertEqual(values['gtk-theme'],original['gtk-theme'])
        self.assertEqual(values['icon-theme'],"'CustomIconTheme'")
        self.assertFalse((self.state/'gtk-restore.json').exists())


if __name__=='__main__': unittest.main()
