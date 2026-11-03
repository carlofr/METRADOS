# Metodología de presupuesto de obra

### Secuencia

1. Metrado por partida, con sustento gráfico y regla normativa.
2. APU por recurso = sumatoria de (cantidad de recurso por unidad de partida × costo unitario del recurso), en S/.
3. Precio parcial de partida = metrado × APU, redondeado a céntimos.
4. Costo directo = sumatoria de parciales de partidas.
5. Gastos generales y utilidad: porcentajes **ingresados por el usuario** sobre el costo directo, de acuerdo con sustento contractual.
6. Subtotal = costo directo + gastos generales + utilidad.
7. IGV: porcentaje ingresado por usuario sobre el subtotal conforme a las condiciones tributarias aplicables.
8. Presupuesto total = subtotal + IGV.

Los porcentajes predeterminados del software son **0%** para evitar suponer condiciones contractuales. **Cero predeterminado no significa que los conceptos no correspondan**. Se exige revisión profesional de incidencia, modalidad de ejecución, vigencia tributaria, rendimientos, fletes, equipos, mano de obra, seguridad, contingencias y costos específicos.

### Redondeos y controles

- Cantidades de metrado: 4 decimales por código presupuestal.
- APU por partida: 4 decimales (S/ por unidad).
- Parciales y resumen monetario: 2 decimales; redondeo HALF_UP.
- El cálculo usa Decimal de Python; no usa aritmética de coma flotante.
- Un código de metrado sin APU produce error; un APU desconocido también produce error para evitar presupuestos incompletos.
- Este flujo genera un presupuesto **referencial de ejemplo**. No genera valorizaciones de ejecución, reajustes polinómicos ni se declara compatible automáticamente con un régimen específico de contratación.

Para cifras de un expediente, use precios sustentados para localidad y fecha y un responsable técnico.
