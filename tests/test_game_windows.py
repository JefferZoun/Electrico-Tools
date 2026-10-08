"""Regresiones de las appXP SDL reales (Windows con escritorio disponible)."""
import sys
import time
import unittest
import tkinter as tk
from electrico.desktop import DesktopApp
from electrico.theme import configure_theme


@unittest.skipUnless(sys.platform=="win32","Integración nativa de Windows")
class GameWindowTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root=tk.Tk()
        except tk.TclError as error:
            self.skipTest(str(error))
        self.root.geometry("900x800")
        configure_theme(self.root)
        self.errors=[]
        self.root.report_callback_exception=lambda *args:self.errors.append(args)
        self.desktop=DesktopApp(self.root)
        self.pump(.15)

    def tearDown(self):
        self.desktop.shutdown()
        self.assertFalse(self.errors,self.errors)

    def pump(self,seconds):
        end=time.perf_counter()+seconds
        while time.perf_counter()<end:
            self.root.update()
            time.sleep(.001)

    def open(self,key):
        self.desktop.open_tool(key)
        self.pump(.15)
        return self.desktop.apps[key]

    def test_continue_survives_false_sdl_focus_loss(self):
        from juegos.sdl_viewport import pygame
        app=self.open("pinball")
        app.on_minimize()
        app.canvas.has_focus=lambda:False
        app.toggle()
        pygame.event.post(pygame.event.Event(pygame.WINDOWFOCUSLOST,window=app.canvas.window))
        self.pump(.25)
        self.assertFalse(app.game.paused)
        app.launch()
        self.pump(.2)
        self.assertEqual(app.game.state,"playing")
        self.assertGreater(app.game.elapsed,0)
        app.key_down("p")
        self.assertTrue(app.game.paused)
        app.key_down("p")
        self.assertTrue(app.game.paused)
        app.key_up("p")
        app.key_down("p")
        self.assertFalse(app.game.paused)

    def test_taskbar_restores_maximized_paused_field_repeatedly(self):
        import ctypes
        app=self.open("pinball")
        self.desktop.chromes["pinball"].toggle_maximize()
        self.pump(.1)
        app.game.score=1234
        draws=[]
        original=app.canvas.draw
        def draw(game):
            draws.append(game.score)
            original(game)
        app.canvas.draw=draw
        user32=app.canvas.user32
        user32.IsWindowVisible.argtypes=[ctypes.c_void_p]
        for _ in range(3):
            self.desktop.toggle_task("pinball")
            self.pump(.08)
            self.assertTrue(app.canvas.suspended)
            self.assertTrue(app.game.paused)
            draws.clear()
            self.desktop.toggle_task("pinball")
            self.pump(.2)
            self.assertIs(self.desktop.apps["pinball"],app)
            self.assertTrue(self.desktop.chromes["pinball"].maximized)
            self.assertFalse(app.canvas.suspended)
            self.assertTrue(user32.IsWindowVisible(app.canvas.window.handle))
            self.assertGreater(app.canvas.renderer.get_viewport().height,0)
            self.assertGreaterEqual(len(draws),2)
            self.assertEqual(app.game.score,1234)
            app.toggle()
            self.pump(.1)
            self.assertFalse(app.game.paused)

    def test_opening_game_closes_other_even_when_hidden(self):
        from juegos.sdl_viewport import SDLViewport
        first=self.open("pong")
        self.desktop.minimize_tool("pong")
        self.pump(.08)
        second=self.open("pinball")
        self.assertNotIn("pong",self.desktop.windows)
        self.assertIsNone(first.canvas.window)
        self.assertIsNone(first.job)
        self.assertEqual(len(SDLViewport.instances),1)
        self.open("pinball")
        self.assertIs(self.desktop.apps["pinball"],second)
        self.open("pong")
        self.assertNotIn("pinball",self.desktop.windows)
        self.assertIsNone(second.canvas.window)
        self.assertEqual(len(SDLViewport.instances),1)

    def test_flappy_controls_restore_and_replaces_other_games(self):
        from juegos.sdl_viewport import pygame,SDLViewport
        pinball=self.open("pinball")
        app=self.open("flappy")
        self.assertNotIn("pinball",self.desktop.windows)
        self.assertIsNone(pinball.canvas.window)
        app.key_down("space")
        app.key_up("space")
        self.pump(.1)
        self.assertEqual(app.game.state,"playing")
        self.assertLess(app.game.y,240)
        app.game.score=4
        self.desktop.toggle_task("flappy")
        self.pump(.08)
        self.assertTrue(app.canvas.suspended)
        self.desktop.toggle_task("flappy")
        self.pump(.15)
        self.assertFalse(app.canvas.suspended)
        self.assertEqual(app.game.score,4)
        app.toggle()
        pygame.event.post(pygame.event.Event(pygame.WINDOWFOCUSLOST,window=app.canvas.window))
        self.pump(.1)
        self.assertFalse(app.game.paused)
        self.desktop.chromes["flappy"].toggle_maximize()
        self.pump(.1)
        self.assertGreater(app.canvas.renderer.get_viewport().height,0)
        self.open("pong")
        self.assertNotIn("flappy",self.desktop.windows)
        self.assertIsNone(app.job)
        self.assertEqual(len(SDLViewport.instances),1)

    def test_home_restores_pong_and_keeps_calculator(self):
        game=self.open("pong")
        calculator=self.open("resistencias")
        self.assertTrue(game.game.paused)
        self.desktop.return_home("pong")
        self.pump(.08)
        self.assertTrue(game.canvas.suspended)
        self.open("pong")
        self.assertFalse(game.canvas.suspended)
        game.canvas.has_focus=lambda:False
        game.toggle()
        self.pump(.2)
        self.assertFalse(game.game.paused)
        self.assertIs(self.desktop.apps["resistencias"],calculator)


if __name__=="__main__":unittest.main()
