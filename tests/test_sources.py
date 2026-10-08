import unittest
from fuentes.model import Generator, associate, parse_number


class AssociationTests(unittest.TestCase):
    def test_series_with_opposition(self):
        result=associate([Generator("G1",12,0.2),Generator("G2",6,0.3),Generator("G3",3,0.5,-1)],"serie")
        self.assertEqual(result.voltage,15)
        self.assertEqual(result.resistance,1)

    def test_identical_parallel(self):
        result=associate([Generator("G1",12,2),Generator("G2",12,2)],"paralelo")
        self.assertEqual(result.voltage,12)
        self.assertEqual(result.resistance,1)

    def test_unequal_parallel(self):
        result=associate([Generator("G1",12,1),Generator("G2",6,2)],"paralelo")
        self.assertEqual(result.voltage,10)
        self.assertAlmostEqual(result.resistance,2/3)

    def test_parallel_obeys_kirchhoff_at_no_load(self):
        generators=[Generator("G1",24,3),Generator("G2",9,2),Generator("G3",6,4,-1)]
        result=associate(generators,"paralelo")
        self.assertAlmostEqual(sum((g.emf-result.voltage)/g.resistance for g in generators),0)

    def test_equal_ideal_parallel(self):
        result=associate([Generator("G1",12),Generator("G2",12)],"paralelo")
        self.assertEqual((result.voltage,result.resistance),(12,0))

    def test_incompatible_ideal_parallel(self):
        for g2 in [Generator("G2",6),Generator("G2",12,0,-1)]:
            with self.assertRaises(ValueError):
                associate([Generator("G1",12),g2],"paralelo")

    def test_ideal_with_real_branch(self):
        result=associate([Generator("G1",12),Generator("G2",6,2)],"paralelo")
        self.assertEqual((result.voltage,result.resistance),(12,0))

    def test_negative_equivalent(self):
        result=associate([Generator("G1",12,1,-1),Generator("G2",3,1)],"serie")
        self.assertEqual(result.voltage,-9)

    def test_opposing_real_sources(self):
        result=associate([Generator("G1",12,1),Generator("G2",12,1,-1)],"paralelo")
        self.assertEqual(result.voltage,0)
        self.assertEqual(result.resistance,0.5)

    def test_single_generator(self):
        for mode in ("serie","paralelo"):
            result=associate([Generator("G1",5,2,-1)],mode)
            self.assertEqual((result.voltage,result.resistance),(-5,2))

    def test_empty_and_invalid_mode(self):
        with self.assertRaises(ValueError):
            associate([],"serie")
        with self.assertRaises(ValueError):
            associate([Generator("G1",1)],"otro")

    def test_invalid_generator_data(self):
        for g in [Generator("G",-1),Generator("G",1,-2),Generator("G",float("nan")),Generator("G",1,0,2)]:
            with self.subTest(g=g),self.assertRaises(ValueError):
                associate([g],"serie")

    def test_decimal_comma_and_units(self):
        self.assertEqual(parse_number("1,5",1000),1500)
        self.assertEqual(parse_number("500",0.001),0.5)
        for text in ["", "abc", "nan", "inf", "-1"]:
            with self.subTest(text=text),self.assertRaises(ValueError):
                parse_number(text)

    def test_large_parallel_values(self):
        result=associate([Generator("G1",1e308,1),Generator("G2",1e308,1)],"paralelo")
        self.assertEqual(result.voltage,1e308)
        self.assertEqual(result.resistance,0.5)

    def test_series_overflow(self):
        with self.assertRaises(ValueError):
            associate([Generator("G1",1e308),Generator("G2",1e308)],"serie")



class LoadTests(unittest.TestCase):
    def test_current_with_real_source(self):
        result=associate([Generator("G1",12,0.1)],"serie",10)
        self.assertAlmostEqual(result.current,12/10.1)
        self.assertAlmostEqual(result.terminal_voltage,result.current*10)

    def test_parallel_load_obeys_kirchhoff(self):
        generators=[Generator("G1",12,1),Generator("G2",6,2)]
        result=associate(generators,"paralelo",10)
        self.assertEqual(result.current,0.9375)
        self.assertEqual(result.terminal_voltage,9.375)
        self.assertAlmostEqual(sum((g.emf-result.terminal_voltage)/g.resistance for g in generators),result.current)

    def test_open_circuit_has_no_load_current(self):
        result=associate([Generator("G1",12,1),Generator("G2",6,2)],"paralelo")
        self.assertEqual(result.current,0)
        self.assertEqual(result.terminal_voltage,10)

    def test_real_short_circuit(self):
        result=associate([Generator("G1",12,2)],"serie",0)
        self.assertEqual(result.current,6)
        self.assertEqual(result.terminal_voltage,0)

    def test_ideal_short_circuit_rejected(self):
        for voltage in (0,12):
            with self.assertRaises(ValueError):
                associate([Generator("G1",voltage)],"serie",0)

    def test_inverse_current(self):
        result=associate([Generator("G1",12,2,-1)],"serie",4)
        self.assertEqual(result.current,-2)
        self.assertEqual(result.terminal_voltage,-8)

    def test_invalid_load(self):
        for value in (-1,float("nan"),float("inf")):
            with self.assertRaises(ValueError):
                associate([Generator("G1",12)],"serie",value)

    def test_large_total_resistance(self):
        result=associate([Generator("G1",1e308,1e308)],"serie",1e308)
        self.assertEqual(result.current,0.5)
        self.assertEqual(result.terminal_voltage,5e307)


if __name__=="__main__":
    unittest.main()
