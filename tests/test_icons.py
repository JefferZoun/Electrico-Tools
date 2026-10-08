import json
import tempfile
import unittest
from pathlib import Path
from electrico.icons import IconLayout,DEFAULT_POSITIONS


class IconTests(unittest.TestCase):
    def test_drag_is_clamped_above_taskbar(self):
        with tempfile.TemporaryDirectory() as folder:
            layout=IconLayout(Path(folder)/"desktop.json")
            self.assertEqual(layout.move("pong",9999,9999,480,500),(378,392))
            self.assertEqual(layout.move("pong",-10,-50,480,500),(14,10))

    def test_positions_survive_reload(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"desktop.json"
            layout=IconLayout(path)
            layout.move("pinball",350,210,800,700)
            self.assertTrue(layout.save())
            self.assertEqual(IconLayout(path).positions["pinball"],(350,210))

    def test_resize_preserves_preferred_position(self):
        with tempfile.TemporaryDirectory() as folder:
            layout=IconLayout(Path(folder)/"desktop.json")
            layout.move("pinball",1500,800,1920,1040)
            self.assertEqual(layout.visible("pinball",480,500),(378,392))
            self.assertEqual(layout.visible("pinball",1920,1040),(1500,800))

    def test_invalid_preferences_are_ignored(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"desktop.json"
            path.write_text('{broken',encoding="utf-8")
            self.assertEqual(IconLayout(path).positions,DEFAULT_POSITIONS)
            path.write_text(json.dumps({"pong":[True,12],"pinball":[float("nan"),20],"unknown":[1,2]}),encoding="utf-8")
            self.assertEqual(IconLayout(path).positions,DEFAULT_POSITIONS)


if __name__=="__main__":unittest.main()
