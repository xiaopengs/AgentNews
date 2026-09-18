import tempfile
import unittest
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw
import generate as g


class LayoutTests(unittest.TestCase):
    def setUp(self):
        self.draw = ImageDraw.Draw(Image.new('RGB', (1024, 1536)))
        self.projects = [dict(full_name=name, owner=name.split('/')[0],
                              name=name.split('/')[1], language='Python',
                              stars=12345, forks=1234, today_stars=3607)
                         for name in g.CURATED_TAGS]

    def test_six_cards_inside_canvas(self):
        for i, (x0, y0, x1, y1) in enumerate(g.CARD_BOXES):
            self.assertTrue(0 <= x0 < x1 < g.IMG_W)
            self.assertTrue(258 < y0 < y1 < 1458)
            if i:
                self.assertGreater(y0, g.CARD_BOXES[i-1][3])

    def test_wrapping_preserves_content(self):
        for value in g.CURATED_DESCRIPTIONS.values():
            lines = g.wrap_text(self.draw, value, g.font(16), 570)
            self.assertEqual(''.join(lines).replace(' ', ''), value.replace(' ', ''))
            for line in lines:
                self.assertLessEqual(self.draw.textlength(line, font=g.font(16)), 570)
                self.assertNotIn(line[0], '，。；：！？、）》】”’')

    def test_rank_is_visually_centered(self):
        for rank in range(1, 7):
            image = Image.new('L', (60, 60))
            g.centered(ImageDraw.Draw(image), (5, 5, 55, 55), str(rank), g.font(28, True), 255)
            x0, y0, x1, y1 = image.getbbox()
            self.assertLessEqual(abs((x0+x1)/2-30), 1)
            self.assertLessEqual(abs((y0+y1)/2-30), 1)

    def test_image_scaling_preserves_circle(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Image.new('RGB', (300, 100), 'white')
            ImageDraw.Draw(source).ellipse((125,25,175,75), fill='black')
            path = Path(tmp)/'circle.png'
            source.save(path)
            dest = Image.new('RGB', (200, 100), 'white')
            g.paste_asset(dest, path, (0,0,200,100))
            mask = dest.convert('L').point(lambda x: 255 if x < 50 else 0)
            x0,y0,x1,y1 = mask.getbbox()
            self.assertLessEqual(abs((x1-x0)-(y1-y0)), 1)

    def test_render_and_overflow_rejection(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'daily.png'
            g.generate_image(self.projects,path,datetime(2026,9,18))
            with Image.open(path) as image:
                self.assertEqual(image.size,(1024,1536))
            self.projects[0]['name'] = 'X'*200
            with self.assertRaises(ValueError):
                g.generate_image(self.projects,path)

    def test_selection_keeps_included_project(self):
        chosen = g.select_top_projects(list(reversed(self.projects)),
                                      'https://github.com/TencentCloud/Octop')
        self.assertEqual(chosen[0]['full_name'], 'TencentCloud/Octop')
        self.assertEqual(len({p['full_name'] for p in chosen}), 6)


if __name__ == '__main__':
    unittest.main()
