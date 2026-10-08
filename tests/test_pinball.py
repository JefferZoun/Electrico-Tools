import math
import unittest
from juegos.pinball_model import PinballGame,BUMPERS


class PinballTests(unittest.TestCase):
    def test_three_balls_and_ready_state(self):
        g=PinballGame()
        self.assertEqual(g.balls_left,3)
        self.assertEqual(g.state,"ready")
        before=(g.x,g.y)
        g.step(.05)
        self.assertEqual(before,(g.x,g.y))

    def test_charged_launch_is_stronger(self):
        a,b=PinballGame(),PinballGame()
        a.launch()
        b.start_charge()
        for _ in range(20):b.step(.05)
        self.assertEqual(b.charge,1)
        b.launch()
        self.assertLess(b.vy,a.vy)
        self.assertEqual(b.state,"playing")
        self.assertFalse(b.charging)

    def test_basic_launch_enters_main_table(self):
        g=PinballGame();g.launch()
        for _ in range(240):g.step(1/240)
        self.assertLess(g.x,418)
        self.assertLess(g.y,200)
        self.assertEqual(g.state,"playing")

    def test_pause_freezes_physics_and_charge(self):
        g=PinballGame();g.launch();g.paused=True
        before=(g.x,g.y,g.vx,g.vy,g.left_angle)
        g.step(.08,True,True)
        self.assertEqual(before,(g.x,g.y,g.vx,g.vy,g.left_angle))

    def test_wall_reflects_incoming_ball(self):
        g=PinballGame();g.x=38;g.y=300;g.vx=-300
        g.segment((30,155),(30,580),3,.82)
        self.assertGreater(g.vx,0)
        self.assertGreater(g.x,42)

    def test_bumper_scores_once_during_contact(self):
        g=PinballGame();g.state="playing"
        x,y,r=BUMPERS[0]
        g.x,g.y=x,y-r-5;g.vx,g.vy=0,200
        g.step(1/240)
        self.assertEqual(g.score,100)
        self.assertLess(g.vy,0)
        g.x,g.y=x,y-r-5;g.vx,g.vy=0,200
        g.step(1/240)
        self.assertEqual(g.score,100)

    def test_targets_complete_mission_and_multiplier(self):
        from juegos.pinball_model import TARGETS
        g=PinballGame();g.state="playing"
        for x,y,r in TARGETS:
            g.x,g.y=x,y-r-5;g.vx,g.vy=0,100
            g.step(1/240)
        self.assertEqual(g.score,700)
        self.assertEqual(g.multiplier,2)
        self.assertFalse(any(g.targets))

    def test_three_drains_end_game(self):
        g=PinballGame()
        for expected in (2,1,0):
            g.state="playing";g.y=g.HEIGHT+26
            g.step(1/240)
            self.assertEqual(g.balls_left,expected)
        self.assertEqual(g.state,"over")
        g.launch()
        self.assertEqual(g.state,"over")

    def test_flippers_move_and_return(self):
        g=PinballGame()
        idle=g.left_angle
        for _ in range(4):g.step(.05,True,True)
        self.assertAlmostEqual(g.left_angle,-.46)
        self.assertAlmostEqual(g.right_angle,math.pi+.46)
        for _ in range(4):g.step(.05)
        self.assertAlmostEqual(g.left_angle,idle)

    def test_moving_flipper_kicks_ball_up(self):
        g=PinballGame();g.state="playing"
        g.left_angle=0
        g.x,g.y=190,615;g.vx,g.vy=0,250
        for _ in range(10):g.step(1/240,True,False)
        self.assertLess(g.vy,0)

    def test_reset_keeps_best_and_clears_match(self):
        g=PinballGame();g.add_score(300);g.reset()
        self.assertEqual(g.best,300)
        self.assertEqual(g.score,0)
        self.assertEqual(g.balls_left,3)

    def test_long_simulation_remains_finite(self):
        g=PinballGame();g.launch()
        for i in range(24000):
            if g.state=="ready":g.launch()
            if g.state=="over":g.reset();g.launch()
            g.step(1/240,(i//60)%2==0,(i//73)%2==0)
            self.assertTrue(all(math.isfinite(v) for v in (g.x,g.y,g.vx,g.vy)))
            self.assertLessEqual(math.hypot(g.vx,g.vy),1300.001)
            self.assertGreaterEqual(g.balls_left,0)


if __name__=="__main__":unittest.main()
