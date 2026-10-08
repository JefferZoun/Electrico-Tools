import random
import unittest
from juegos.flappy_model import FlappyGame,ElectricPost


class FlappyTests(unittest.TestCase):
    def game(self):return FlappyGame(random.Random(12))

    def test_ready_does_not_fall(self):
        g=self.game();g.step(.08)
        self.assertEqual((g.y,g.vy,g.state),(240,0,"ready"))

    def test_flap_starts_and_gravity_then_slows_ascent(self):
        g=self.game();g.flap();g.step(.05)
        self.assertEqual(g.state,"playing")
        self.assertLess(g.y,240)
        self.assertGreater(g.vy,g.FLAP_SPEED)
        g.flap();self.assertEqual(g.vy,g.FLAP_SPEED)

    def test_pause_freezes_bird_obstacles_and_score(self):
        g=self.game();g.flap();g.paused=True
        snapshot=(g.y,g.vy,g.posts[0].x,g.score)
        g.flap();g.step(.08)
        self.assertEqual(snapshot,(g.y,g.vy,g.posts[0].x,g.score))

    def test_ground_and_ceiling_end_flight(self):
        for y in (10,455):
            g=self.game();g.state="playing";g.y=y
            g.step(1/240)
            self.assertEqual(g.state,"over")

    def test_mast_collision_ends_flight(self):
        g=self.game();g.state="playing";g.y=50
        g.posts=[ElectricPost(g.BIRD_X-42,250),ElectricPost(600,250)]
        g.step(1/240)
        self.assertEqual(g.state,"over")

    def test_gap_is_clear(self):
        g=self.game();g.state="playing";g.y=250
        g.posts=[ElectricPost(g.BIRD_X-42,250),ElectricPost(600,250)]
        g.step(1/240)
        self.assertEqual(g.state,"playing")

    def test_empty_space_next_to_mast_is_not_a_collision(self):
        g=self.game();g.y=40
        post=ElectricPost(g.BIRD_X+2,250)
        self.assertFalse(any(g.intersects(rect) for rect in g.post_rectangles(post)))

    def test_passing_post_counts_once(self):
        g=self.game();g.state="playing"
        post=ElectricPost(g.BIRD_X-g.RADIUS-g.POST_WIDTH-1,240)
        g.posts=[post,ElectricPost(600,240)]
        g.step(1/240);g.step(1/240)
        self.assertEqual(g.score,1)
        self.assertEqual(g.best,1)
        self.assertTrue(post.scored)

    def test_restart_clears_score_and_preserves_best(self):
        g=self.game();g.best=7;g.score=3;g.state="over"
        g.flap()
        self.assertEqual(g.best,7)
        self.assertEqual(g.score,0)
        self.assertEqual(g.state,"playing")
        self.assertEqual(g.vy,g.FLAP_SPEED)

    def test_difficulty_rises_in_steps_and_stays_bounded(self):
        g=self.game()
        self.assertEqual((g.level,g.target_speed,g.gap_size,g.spacing),(1,215,155,260))
        g.score=5
        self.assertEqual((g.level,g.target_speed,g.gap_size,g.spacing),(2,224,151,257))
        g.score=500
        self.assertEqual((g.level,g.target_speed,g.gap_size,g.spacing),(11,305,115,230))

    def test_existing_obstacles_keep_their_gap_when_level_changes(self):
        g=self.game()
        old=g.posts[-1]
        original=old.gap_size
        g.score=25
        g.state="playing"
        g.posts[0].x=-90
        g.posts[1].x=185
        g.posts[2].x=460
        g.step(1/240)
        self.assertEqual(old.gap_size,original)
        self.assertEqual(g.posts[-1].gap_size,g.gap_size)
        self.assertIsNotNone(g.previous_post)
        self.assertLessEqual(abs(g.posts[-1].gap_y-old.gap_y),100)

    def test_speed_increases_smoothly_and_freezes_on_pause(self):
        g=self.game();g.score=50;g.state="playing"
        g.step(.08)
        self.assertGreater(g.speed,g.SPEED)
        self.assertLess(g.speed,g.target_speed)
        before=(g.speed,g.distance,g.posts[0].x)
        g.paused=True;g.step(.08)
        self.assertEqual((g.speed,g.distance,g.posts[0].x),before)
        g.reset()
        self.assertEqual((g.speed,g.distance,g.level),(g.SPEED,0,1))

    def test_next_post_waits_outside_screen_before_visible_one_leaves(self):
        g=self.game()
        self.assertLess(g.posts[0].x,g.WIDTH)
        self.assertGreaterEqual(g.posts[-1].x,g.WIDTH+g.SPACING)
        g.state="playing"
        g.score=4
        g.posts=[ElectricPost(80,250),ElectricPost(340,250),ElectricPost(600,250)]
        g.step(1/240)
        self.assertGreaterEqual(g.posts[-1].x,g.WIDTH+g.SPACING)
        self.assertTrue(any(g.WIDTH<=post.x<g.WIDTH+g.SPACING for post in g.posts))

    def test_post_buffer_is_filled_even_on_a_fatal_frame(self):
        g=self.game();g.state="playing";g.y=g.FLOOR-10
        g.posts=[ElectricPost(80,250),ElectricPost(340,250),ElectricPost(600,250)]
        g.step(1/240)
        self.assertEqual(g.state,"over")
        self.assertGreaterEqual(g.posts[-1].x,g.WIDTH+g.SPACING)

    def test_recycled_posts_keep_spacing_and_valid_gap(self):
        g=self.game();g.state="playing"
        g.posts=[ElectricPost(-90,250,True),ElectricPost(185,250),ElectricPost(460,250)]
        g.step(1/240)
        self.assertGreater(len(g.posts),3)
        self.assertAlmostEqual(g.posts[-1].x-g.posts[-2].x,g.SPACING)
        self.assertGreaterEqual(g.posts[-1].x,g.WIDTH+g.SPACING)
        self.assertGreaterEqual(g.posts[-1].gap_y,135)
        self.assertLessEqual(g.posts[-1].gap_y,323)


if __name__=="__main__":unittest.main()
