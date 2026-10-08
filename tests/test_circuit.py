import unittest
from resistencias.circuit import Group, Resistor, calculate, parse_resistance

class CircuitTests(unittest.TestCase):
    def test_series(self):
        self.assertEqual(calculate(Group("S", "serie", [Resistor("R1", 100), Resistor("R2", 200)])).value, 300)

    def test_parallel(self):
        self.assertAlmostEqual(calculate(Group("P", "paralelo", [Resistor("R1", 200), Resistor("R2", 300)])).value, 120)

    def test_mixed_step_order(self):
        inner = Group("P", "paralelo", [Resistor("R2", 200), Resistor("R3", 300)])
        result = calculate(Group("S", "serie", [Resistor("R1", 100), inner]))
        self.assertEqual(result.value, 220)
        self.assertTrue(result.steps[0].startswith("P"))
        self.assertTrue(result.steps[1].startswith("S"))
        self.assertIn("R2", result.steps[0])

    def test_parallel_of_series(self):
        circuit = Group("P", "paralelo", [Group("S1", "serie", [Resistor("R1", 100), Resistor("R2", 100)]), Group("S2", "serie", [Resistor("R3", 200), Resistor("R4", 200)])])
        self.assertAlmostEqual(calculate(circuit).value, 400 / 3)

    def test_short_circuit(self):
        self.assertEqual(calculate(Group("P", "paralelo", [Resistor("R1", 0), Resistor("R2", 100)])).value, 0)

    def test_single_resistor(self):
        for mode in ("serie", "paralelo"):
            self.assertEqual(calculate(Group("G", mode, [Resistor("R1", 50)])).value, 50)

    def test_empty_group_rejected(self):
        with self.assertRaises(ValueError):
            calculate(Group("vacío"))
        with self.assertRaises(ValueError):
            calculate(Group("raíz", children=[Resistor("R1", 10), Group("vacío")]))

    def test_units(self):
        self.assertEqual(parse_resistance(" 1,5 ", "kΩ"), 1500)
        self.assertEqual(parse_resistance("2", "MΩ"), 2_000_000)
        self.assertEqual(parse_resistance("0"), 0)

    def test_invalid_inputs(self):
        for value in ("", "texto", "-1", "nan", "inf", "1e999"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_resistance(value)

    def test_extremes(self):
        result = calculate(Group("P", "paralelo", [Resistor("R1", 1e-300), Resistor("R2", 1e-300)]))
        self.assertAlmostEqual(result.value / 1e-300, 0.5)
        with self.assertRaises(ValueError):
            calculate(Group("S", "serie", [Resistor("R1", 1e308), Resistor("R2", 1e308)]))

    def test_invalid_model(self):
        with self.assertRaises(ValueError):
            calculate(Resistor("R", -5))
        with self.assertRaises(ValueError):
            calculate(Group("G", "otro", [Resistor("R", 5)]))

if __name__ == "__main__":
    unittest.main()
