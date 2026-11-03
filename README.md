# METRADOS | Perú
## Metrados y presupuestos de obras de edificación

Repositorio abierto para documentar partidas según la **Norma Técnica Metrados para Obras de Edificación y Habilitaciones Urbanas** (R.D. N.° 073-2010/VIVIENDA/VMCS-DNC), calcular cantidades geométricas trazables y elaborar un presupuesto ilustrativo a partir de análisis de precios unitarios (APU).

**Estado:** versión inicial funcional (v0.1), no expediente técnico ni herramienta de certificación normativa. No incluye metrados de un proyecto real, precios de mercado ni verificación automática de todas las reglas de medición. Se requiere revisión y firma del profesional responsable.

### Directorios

| Ruta | Contenido |
| --- | --- |
| reglamento/ | Fuentes oficiales, estructura OE/HU, límites y controles normativos |
| metrados/ | Guías por especialidad: preliminares, estructuras, arquitectura, sanitarias, eléctricas, comunicaciones, gas y habilitaciones urbanas |
| plantillas/ | CSV vacíos para metrado geométrico y recursos de APU |
| ejemplos/ | Datos **ficticios**, únicamente para probar el flujo |
| scripts/ | Motor de cálculo en Python estándar, sin dependencias externas |
| presupuesto/ | Metodología de APU y consolidación económica |
| documentacion/ | Alcance, control de calidad y hoja de ruta |
| tests/ | Pruebas automáticas de fórmulas y validaciones |
| .github/workflows/ | Pruebas continuas en GitHub Actions |

### Requisitos

Python 3.11 o superior. No se requiere instalar paquetes externos. Los CSV pueden editarse también en Excel (guardar como UTF-8, separador coma y decimal punto para el procesamiento).

### Uso rápido

1. Copie plantillas/planilla_metrados.csv y plantillas/apu_recursos.csv a su carpeta de proyecto; registre planos, partidas y precios debidamente sustentados.
2. Para probar sin datos reales:

   python scripts/calcular.py metrados --entrada ejemplos/planilla_metrados.csv --salida resultados/metrados.csv

   python scripts/calcular.py presupuesto --metrados resultados/metrados.csv --apu ejemplos/apu_recursos.csv --salida resultados/presupuesto.csv --resumen resultados/resumen.json

3. Revise los resultados, las unidades y la correspondencia con los planos. Los ejemplos utilizan costos ficticios y porcentajes indirectos por defecto en cero.
4. Al calcular un proyecto real, indique los porcentajes validados de gastos generales, utilidad e IGV según modalidad, base tributaria y expediente. Consulte presupuesto/README.md.
5. Ejecute las pruebas:

   python -m unittest discover -s tests -v

### Cómo funciona

- La planilla usa cuatro operaciones geométricas: longitud (m), área (m2), volumen (m3) y conteo (und). No reemplazan la **forma de medición** ni las reglas de deducción exigidas por cada partida en la norma.
- Cada fila requiere código presupuestal único por tipo de partida, descripción, referencia a plano, unidad y dimensiones. El código presupuestal es interno (p. ej. EST-001), **no es un código normativo OE**; registre el código OE aplicable en la documentación técnica del expediente.
- Los metrados se consolidan por código. No se permite mezclar descripciones o unidades con el mismo código.
- El APU se calcula sumando cantidad de recurso por unidad de partida × precio del recurso. El presupuesto es metrado × precio unitario.
- Se reportan montos en S/ con redondeo financiero explícito. No se sustituyen verificaciones estructurales, instalaciones ni rendimientos de obra.

### Fuentes principales

- [Norma Técnica de Metrados – RD 073-2010 (copia alojada en SPIJ/Minjus)](https://spij.minjus.gob.pe/Graficos/Peru/2011/Mayo/18/RD-073-2010-VIVIENDA-VMCS-DNC.pdf)
- [Reglamento Nacional de Edificaciones – MVCS](https://www.gob.pe/institucion/vivienda/informes-publicaciones/2309793-reglamento-nacional-de-edificaciones-rne)
- [Actualización de E.030 – RM 183-2026-VIVIENDA](https://www.gob.pe/institucion/vivienda/normas-legales/8081915-183-2026-vivienda)
- [Modificación transitoria de E.030 – RM 217-2026-VIVIENDA](https://www.gob.pe/institucion/vivienda/normas-legales/8219609-217-2026-vivienda)

La norma de metrados (códigos OE/HU) y el RNE (diseño y ejecución) son instrumentos **distintos**. Consulte reglamento/REFERENCIAS_NORMATIVAS.md antes de elaborar un presupuesto.

### Licencia y procedencia

El código y la documentación original se distribuyen bajo MIT (LICENSE, ya existente). Los documentos oficiales enlazados y los aportes de terceros mantienen sus respectivos derechos. No se redistribuye el PDF normativo.

### Colaboración

Revise CONTRIBUTING.md. No publique datos personales, planos confidenciales ni precios contractuales sensibles sin autorización.
