"""Pruebas reproducibles sin dependencias externas."""
import csv
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from calcular import ErrorDatos, lee_csv, metrados, presupuesto, CAMPOS_METRADO, CAMPOS_APU  # noqa: E402


class PruebasMetrados(unittest.TestCase):
    def setUp(self):
        self.filas = lee_csv(ROOT / "ejemplos" / "planilla_metrados.csv", CAMPOS_METRADO)
        self.apu = lee_csv(ROOT / "ejemplos" / "apu_recursos.csv", CAMPOS_APU)

    def test_cantidades_ejemplo(self):
        valores = {f["codigo"]: f["cantidad"] for f in metrados(self.filas)}
        self.assertEqual(valores, {"PRE-001": "18.0000", "EST-001": "2.2500",
                                  "ARQ-001": "20.8000", "SAN-001": "15.4000",
                                  "ELE-001": "12.0000"})

    def test_consolidacion_y_descuento(self):
        filas = [dict(self.filas[0]), dict(self.filas[0])]
        filas[0]["descuento"] = "1"
        filas[1]["descuento"] = "2"
        self.assertEqual(metrados(filas)[0]["cantidad"], "33.0000")

    def test_unidad_incorrecta(self):
        fila = dict(self.filas[0], unidad="m2")
        with self.assertRaisesRegex(ErrorDatos, "exige unidad"):
            metrados([fila])

    def test_descuento_excesivo(self):
        fila = dict(self.filas[1], descuento="3")
        with self.assertRaisesRegex(ErrorDatos, "descuento"):
            metrados([fila])

    def test_codigo_inconsistente(self):
        fila = dict(self.filas[0], partida="Otra partida")
        with self.assertRaisesRegex(ErrorDatos, "duplicado"):
            metrados([self.filas[0], fila])

    def test_repeticiones_enteras(self):
        fila = dict(self.filas[0], repeticiones="1.5")
        with self.assertRaisesRegex(ErrorDatos, "entero"):
            metrados([fila])

    def test_nan_invalido(self):
        fila = dict(self.filas[0], largo_m="NaN")
        with self.assertRaises(ErrorDatos):
            metrados([fila])

    def test_total_con_impuesto(self):
        datos, resumen = presupuesto(metrados(self.filas), self.apu,
                                    Decimal("10"), Decimal("5"), Decimal("18"))
        self.assertEqual(len(datos), 5)
        # PRE: 18*44.4=799.20; EST: 2.25*440=990.00
        # ARQ: 20.8*15.4=320.32; SAN:15.4*21=323.40; ELE:12*28=336.00
        self.assertEqual(resumen["costo_directo_pen"], "2768.92")
        self.assertEqual(resumen["gastos_generales_pen"], "276.89")
        self.assertEqual(resumen["utilidad_pen"], "138.45")
        self.assertEqual(resumen["subtotal_pen"], "3184.26")
        self.assertEqual(resumen["igv_pen"], "573.17")
        self.assertEqual(resumen["presupuesto_total_pen"], "3757.43")

    def test_falta_apu(self):
        with self.assertRaisesRegex(ErrorDatos, "sin APU"):
            presupuesto(metrados(self.filas), self.apu[:-2])

    def test_porcentaje_invalido(self):
        with self.assertRaisesRegex(ErrorDatos, "porcentaje"):
            presupuesto(metrados(self.filas), self.apu, Decimal("101"))

    def test_cli_extremo_a_extremo(self):
        with tempfile.TemporaryDirectory() as tmp:
            cantidad = Path(tmp) / "cantidades.csv"
            presupuesto_csv = Path(tmp) / "presupuesto.csv"
            resumen = Path(tmp) / "resumen.json"
            for comando in [
                [sys.executable, str(ROOT / "scripts" / "calcular.py"), "metrados",
                 "--entrada", str(ROOT / "ejemplos" / "planilla_metrados.csv"),
                 "--salida", str(cantidad)],
                [sys.executable, str(ROOT / "scripts" / "calcular.py"), "presupuesto",
                 "--metrados", str(cantidad),
                 "--apu", str(ROOT / "ejemplos" / "apu_recursos.csv"),
                 "--salida", str(presupuesto_csv), "--resumen", str(resumen)]
            ]:
                resultado = subprocess.run(comando, capture_output=True, text=True)
                self.assertEqual(resultado.returncode, 0, resultado.stderr)
            with presupuesto_csv.open(encoding="utf-8", newline="") as fh:
                self.assertEqual(len(list(csv.DictReader(fh))), 5)
            self.assertIn("presupuesto_total_pen", resumen.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
