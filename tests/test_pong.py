import math
import random
import unittest
from juegos.pong_model import PongGame


class PongTests(unittest.TestCase):
    def game(self):
        g=PongGame(random.Random(9))
        g.paused=False
        g.serve_delay=0
        return g

    def test_paused_game_does_not_move(self):
        g=PongGame()
        before=(g.x,g.y,g.player,g.cpu)
        g.step(.1,1)
        self.assertEqual(before,(g.x,g.y,g.player,g.cpu))

    def test_wall_reflects_ball(self):
        g=self.game()
        g.x,g.y,g.vx,g.vy=400,9,100,-300
        g.step(.03)
        self.assertGreater(g.vy,0)
        self.assertGreaterEqual(g.y,g.RADIUS)

    def test_paddle_reflects_fast_ball(self):
        g=self.game()
        g.x,g.y,g.vx,g.vy=60,g.player,-680,0
        g.step(.08)
        self.assertGreater(g.vx,0)
        self.assertEqual((g.player_score,g.cpu_score),(0,0))
        self.assertLessEqual(math.hypot(g.vx,g.vy),g.MAX_SPEED+0.000001)

    def test_miss_scores_only_once_and_serves(self):
        g=self.game()
        g.x,g.y,g.vx,g.vy=10,20,-400,0
        g.step(.1)
        self.assertEqual(g.cpu_score,1)
        self.assertEqual(g.x,400)
        self.assertGreater(g.serve_delay,0)
        g.step(.1)
        self.assertEqual(g.cpu_score,1)

    def test_right_goal_scores_for_player(self):
        g=self.game()
        g.x,g.y,g.vx,g.vy=805,20,400,0
        g.step(.03)
        self.assertEqual(g.player_score,1)
        self.assertEqual(g.cpu_score,0)

    def test_seventh_point_ends_game(self):
        g=self.game()
        g.player_score=6
        g.x,g.y,g.vx,g.vy=805,20,400,0
        g.step(.03)
        self.assertEqual(g.player_score,7)
        self.assertEqual(g.winner,"¡Has ganado!")
        self.assertTrue(g.paused)
        g.toggle_pause()
        self.assertEqual((g.player_score,g.cpu_score),(0,0))
        self.assertIsNone(g.winner)
        self.assertFalse(g.paused)

    def test_input_and_large_time_are_bounded(self):
        g=self.game()
        g.step(100,100)
        self.assertLessEqual(g.player,450-44)
        self.assertLessEqual(abs(g.x-400),68)
        for i in range(100): g.step(.1,-1)
        self.assertGreaterEqual(g.player,44)
        self.assertGreaterEqual(g.cpu,44)
        self.assertLessEqual(g.cpu,406)

    def test_ball_speed_stays_in_configured_range(self):
        g=self.game()
        self.assertAlmostEqual(math.hypot(g.vx,g.vy),g.SERVE_SPEED)
        for i in range(100):
            g.y=g.player
            g.bounce(g.player,1)
        self.assertAlmostEqual(math.hypot(g.vx,g.vy),g.MAX_SPEED)
        self.assertEqual(g.SERVE_SPEED,360)
        self.assertEqual(g.MAX_SPEED,720)

    def test_reset_preserves_difficulty(self):
        g=self.game()
        g.difficulty="Difícil"
        g.player_score=4
        g.reset()
        self.assertEqual(g.difficulty,"Difícil")
        self.assertEqual(g.player_score,0)
        self.assertTrue(g.paused)


if __name__=="__main__":
    unittest.main()
