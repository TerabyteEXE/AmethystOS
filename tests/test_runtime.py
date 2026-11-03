"""Hardware-independent tests for Kuhl settings and generated source-based Waybar."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import desktop,render

class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='kuhl-rebase-test-')
        root=Path(self.tmp.name)
        self.data=root/'data/kuhl'; self.state=root/'state/kuhl'; self.config=root/'config'
        self.data.mkdir(parents=True)
        (self.data/'themes.json').write_bytes((ROOT/'config/themes.json').read_bytes())
        self.templates=self.data/'templates'
        import shutil
        shutil.copytree(ROOT/'configs',self.templates)
        self.patcher=patch.multiple(desktop,DATA=self.data,STATE=self.state,CONFIG=self.config,PREF_PATH=self.state/'preferences.json')
        self.patcher.start()
        self.render_patcher=patch.multiple(render,DATA=self.data,STATE=self.state,CONFIG=self.config,MANIFEST=self.state/'managed.json')
        self.render_patcher.start()
    def tearDown(self):
        self.render_patcher.stop();self.patcher.stop();self.tmp.cleanup()
    def test_sidebar_default_scaling_modules(self):
        theme=json.loads((self.data/'themes.json').read_text())['sevens']
        conf,css=desktop.bar_files('sevens',theme)
        j=json.loads(conf)
        self.assertEqual(j['position'],'left')
        self.assertEqual(j['width'],44)
        self.assertIn('niri/workspaces',j['modules-center'])
        self.assertIn('custom/close',j['modules-right'])
        self.assertIn('font-size: 15px',css.decode())
        p=desktop.preferences();p['bar_scale']=1.5;p['bar_position']='right';p['bar_modules']['close']=False
        desktop.save_preferences(p)
        j=json.loads(desktop.bar_files('sevens',theme)[0])
        self.assertEqual(j['width'],66)
        self.assertNotIn('custom/close',j['modules-right'])
        self.assertEqual(j['position'],'right')
        p['bar_position']='top';desktop.save_preferences(p)
        j=json.loads(desktop.bar_files('sevens',theme)[0])
        self.assertEqual(j['height'],54)
        self.assertNotIn('width',j)
    def test_output_scale_does_not_clobber_user_edits(self):
        path=self.config/'niri/output.kdl'
        with patch.object(desktop.shutil,'which',return_value=None):
            desktop.set_output('HDMI-A-1',1.25)
            self.assertIn('scale 1.25',path.read_text())
            before=path.read_text()
            with self.assertRaises(SystemExit):desktop.scale_value('500',.75,3)
            self.assertEqual(path.read_text(),before)
            path.write_text('// custom manual edits\n')
            with self.assertRaises(SystemExit):desktop.set_output('DP-1',1.5)
            self.assertEqual(path.read_text(),'// custom manual edits\n')
    def test_theme_generation_contains_upstream_files_and_fonts(self):
        result=render.theme_files('sevens')
        files={str(k):v.decode() for k,v in result.items()}
        self.assertIn('font_size 12',files[str(self.config/'kitty/kitty.conf')])
        self.assertIn('size = 12',files[str(self.config/'alacritty/alacritty.toml')])
        self.assertIn('JetBrains Mono',files[str(self.config/'rofi/kuhl.rasi')])
        self.assertIn('@define-color color4',files[str(self.config/'waybar/colors.css')])
    def test_gtk_restore(self):
        values={'color-scheme':"'prefer-light'",'gtk-theme':"'Adwaita'",'icon-theme':"'Adwaita'",'text-scaling-factor':'1.0'}
        old=copy.copy(values)
        def call(action,key,value=None):
            if action=='get':return values[key]
            values[key]=value
            return ''
        with patch.object(desktop,'gtk_call',side_effect=call):
            desktop.sync_gtk('sevens')
            self.assertEqual(values['color-scheme'],"'prefer-dark'")
            values['icon-theme']="'UserChosen'"
            desktop.restore_gtk()
        self.assertEqual(values['color-scheme'],old['color-scheme'])
        self.assertEqual(values['icon-theme'],"'UserChosen'")
if __name__=='__main__':unittest.main()
