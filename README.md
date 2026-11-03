# Presupuestos de obra | Perú

Repositorio de trabajo para organizar **partidas, metrados, análisis de precios unitarios (APU), presupuestos y resúmenes de obras de edificación** con trazabilidad a normativa peruana.

> **Estado:** base técnica y plantilla operativa para captura y cálculo. No es un expediente técnico ni presupuesto definitivo. Las cantidades dependen de planos aprobados; los precios, rendimientos, porcentajes e impuestos deben validarse para cada obra y fecha. La publicación en GitHub está pendiente de autenticar la cuenta propietaria.

## Estructura

- `reglamento/`: catálogo CSV inicial con 171 ítems, 67 grupos y referencias verificadas al RNE y a la Norma Técnica de Metrados para Obras de Edificación y Habilitaciones Urbanas; separación expresa entre diseño, seguridad y medición.
- `plantillas/`: inventario y notas sobre plantillas evaluadas.
- `metrados/`: guías técnicas de cómputo organizadas por especialidad (`estructuras`, `arquitectura`, `sanitarias`, `electricas`).
- `presupuesto/`: libro Excel maestro con partidas, metrados, APU, presupuesto y resumen ejecutivo.
- `documentacion/`: decisiones técnicas, instrucciones, estado, datos faltantes, reporte ejecutivo y controles de calidad.
- `scripts/`: utilitarios de comprobación y reconstrucción del libro (en una copia nueva).

## Puesta en marcha

1. Descargue y abra `presupuesto/PRESUPUESTO_OBRA_BASE.xlsx` con Excel compatible con `.xlsx` y cálculo automático.
2. En **Resumen**, complete primero identificación del proyecto y los porcentajes aplicables *validados*. Las celdas de ingreso están en **azul**; los vínculos en **verde** y los controles pendientes en **naranja**.
3. En **Partidas**, elija `SI` en la columna H para los ítems del proyecto. El código OE normativo se conserva en columna A; el código presupuestal único se guarda en G. Para variantes de material o dimensiones revise `documentacion/INSTRUCCIONES_OPERATIVAS.md`.
4. En **Metrados**, registre el **código presupuestal G**, elementos, dimensiones, cantidad, geometría y referencia verificable a plano/memoria. No hay cantidades de obra prefijadas.
5. En **APU**, use el **mismo código presupuestal**, ingrese los recursos reales, unidad, cantidad por unidad de partida y precio unitario; el libro suma automáticamente el costo unitario de cada partida.
6. Revise **Presupuesto** y **Resumen**: las partidas incompletas muestran alertas; las celdas de presupuesto no se consideran resultados finales mientras existan datos pendientes.
7. Verifique con un profesional responsable la correspondencia de especialidades, los criterios de medición, rendimientos, IGV, gastos generales, utilidad y fecha de precios.

## Alcance normativo

El **Reglamento Nacional de Edificaciones (RNE)** define condiciones técnicas de diseño y construcción. Los **códigos OE** usados para la organización de partidas pertenecen a una **norma técnica de metrados distinta del RNE**. Las referencias y límites se documentan en `reglamento/REFERENCIAS_NORMATIVAS.md`. Este repositorio no redistribuye los textos oficiales protegidos ni los sustituye.

## Publicación

Para crear el remoto en `https://github.com/<USUARIO>/presupuestos-de-obra`, consulte `documentacion/PUBLICACION_GITHUB.md`. No asuma que el remoto existe hasta obtener confirmación del servicio GitHub.

## Licencia

El código, las plantillas originales y la documentación propia se distribuyen bajo licencia MIT (`LICENSE`). Las disposiciones legales, normas oficiales y los archivos aportados por terceros conservan su titularidad y condiciones de uso.

## Control de alcance y estado

La entrega actual incluye **238 entradas normativas organizadas (171 ítems medibles y 67 agrupaciones)**. La selección corresponde a una base parcial documentada y no cubre todos los rubros de la NTM ni incorpora precios de mercado. La cuantificación y el presupuesto final continúan pendientes de datos del expediente técnico. Consulte `documentacion/DATOS_REQUERIDOS.md`, `documentacion/RESUMEN_EJECUTIVO.md` y `documentacion/INSTRUCCIONES_OPERATIVAS.md`.

Pruebe la estructura con `python scripts/verificar_libro.py`. La verificación comprueba correspondencia y sintaxis, pero **el recálculo de Excel debe efectuarse al abrir el libro en Microsoft Excel**. Véase `documentacion/CONTROL_CALIDAD.md`.

**No ejecutar `scripts/crear_libro.py` encima de un libro con datos reales: el script reconstruye una plantilla vacía y sobrescribe el archivo.**
