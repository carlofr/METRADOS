# Calculadora por línea de comandos

Motor sin dependencias externas, basado en decimal.Decimal. Ejecutar desde la raíz del repositorio:

```sh
python scripts/calcular.py metrados --entrada ejemplos/planilla_metrados.csv --salida resultados/metrados.csv
python scripts/calcular.py presupuesto --metrados resultados/metrados.csv --apu ejemplos/apu_recursos.csv --salida resultados/presupuesto.csv --resumen resultados/resumen.json --gastos-generales 10 --utilidad 5 --igv 18
python -m unittest discover -s tests -v
```

Los porcentajes anteriores son **sólo demostrativos**, no supuestos normativos o tributarios para una obra real. Los cálculos redondean con HALF_UP. La validación geométrica sólo cubre longitud, área, volumen y conteo, no reglas OE específicas.

El CSV de salida de metrados incluye `codigo,partida,unidad,cantidad,referencias_planos`. La salida de presupuesto incluye `codigo,partida,unidad,metrado,precio_unitario_pen,parcial_pen` y el resumen JSON contiene importes y tasas.

El código presupuestal debe ser único y consistente. No reutilice códigos para cambiar especificación o unidad. Se rechazan valores NaN, negativos, descuentos mayores que la cantidad, unidades incorrectas, APU incompletos y porcentajes fuera de 0 a 100.
