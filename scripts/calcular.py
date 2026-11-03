#!/usr/bin/env python3
"""Motor inicial de metrados y presupuestos en PEN; sólo biblioteca estándar."""
from __future__ import annotations

import argparse
import csv
import json
from collections import OrderedDict
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path


QTY = Decimal("0.0001")
MONEY = Decimal("0.01")
OPERACIONES = {"longitud": ("m", ("largo_m",)),
               "area": ("m2", ("largo_m", "ancho_m")),
               "volumen": ("m3", ("largo_m", "ancho_m", "alto_m")),
               "conteo": ("und", ())}
CAMPOS_METRADO = ["codigo", "partida", "unidad", "operacion", "repeticiones",
                  "largo_m", "ancho_m", "alto_m", "descuento", "ref_plano", "nota"]
CAMPOS_APU = ["codigo", "recurso", "unidad_recurso", "cantidad_por_unidad",
              "precio_recurso_pen", "fuente_precio", "fecha_precio"]
SALIDA_METRADOS = ["codigo", "partida", "unidad", "cantidad", "referencias_planos"]
SALIDA_PRESUPUESTO = ["codigo", "partida", "unidad", "metrado", "precio_unitario_pen", "parcial_pen"]


class ErrorDatos(ValueError):
    """Error verificable de datos de entrada."""


def numero(valor: str, campo: str, *, minimo: Decimal = Decimal(0), estricto: bool = False) -> Decimal:
    if valor is None or str(valor).strip() == "":
        raise ErrorDatos(f"Campo numérico obligatorio vacío: {campo}")
    try:
        v = Decimal(str(valor).strip())
    except (InvalidOperation, ValueError) as exc:
        raise ErrorDatos(f"Valor numérico inválido en {campo}: {valor!r}") from exc
    if not v.is_finite() or v < minimo or (estricto and v == minimo):
        raise ErrorDatos(f"Valor fuera de rango en {campo}: {valor!r}")
    return v


def lee_csv(ruta: str | Path, campos: list[str]) -> list[dict[str, str]]:
    ruta = Path(ruta)
    try:
        with ruta.open("r", encoding="utf-8-sig", newline="") as fh:
            lector = csv.DictReader(fh, strict=True)
            if lector.fieldnames is None or any(c not in lector.fieldnames for c in campos):
                raise ErrorDatos(f"{ruta}: faltan columnas. Requeridas: {', '.join(campos)}")
            datos = list(lector)
    except (UnicodeError, csv.Error) as exc:
        raise ErrorDatos(f"{ruta}: CSV inválido ({exc})") from exc
    if not datos:
        raise ErrorDatos(f"{ruta}: no hay registros")
    for i, fila in enumerate(datos, 2):
        if None in fila or any(k is None for k in fila.values()):
            raise ErrorDatos(f"{ruta}: columna sobrante o valor ausente en fila {i}")
    return datos


def campo(fila: dict[str, str], nombre: str, contexto: str) -> str:
    valor = str(fila.get(nombre) or "").strip()
    if not valor:
        raise ErrorDatos(f"{contexto}: falta {nombre}")
    return valor


def metrados(filas: list[dict[str, str]]) -> list[dict[str, str]]:
    por_codigo: OrderedDict[str, dict[str, object]] = OrderedDict()
    for i, fila in enumerate(filas, 2):
        contexto = f"Metrados fila {i}"
        codigo = campo(fila, "codigo", contexto)
        partida = campo(fila, "partida", contexto)
        unidad = campo(fila, "unidad", contexto)
        operacion = campo(fila, "operacion", contexto).lower()
        plano = campo(fila, "ref_plano", contexto)
        if operacion not in OPERACIONES:
            raise ErrorDatos(f"{contexto}: operación no soportada {operacion!r}")
        unidad_esperada, dimensiones = OPERACIONES[operacion]
        if unidad != unidad_esperada:
            raise ErrorDatos(f"{contexto}: {operacion} exige unidad {unidad_esperada}, no {unidad}")
        repeticiones = numero(fila.get("repeticiones"), f"{contexto}.repeticiones", estricto=True)
        if repeticiones != repeticiones.to_integral_value():
            raise ErrorDatos(f"{contexto}: repeticiones debe ser entero")
        bruto = repeticiones
        for dimension in dimensiones:
            bruto *= numero(fila.get(dimension), f"{contexto}.{dimension}", estricto=True)
        for dimension in set(("largo_m", "ancho_m", "alto_m")) - set(dimensiones):
            if str(fila.get(dimension) or "").strip():
                raise ErrorDatos(f"{contexto}: dimensión inesperada {dimension}")
        descuento = numero(fila.get("descuento") or "0", f"{contexto}.descuento")
        if descuento >= bruto:
            raise ErrorDatos(f"{contexto}: descuento igual o mayor que cantidad bruta")
        cantidad = bruto - descuento
        if codigo not in por_codigo:
            por_codigo[codigo] = {"codigo": codigo, "partida": partida, "unidad": unidad,
                                "cantidad_decimal": Decimal(0), "planos": set()}
        grupo = por_codigo[codigo]
        if grupo["partida"] != partida or grupo["unidad"] != unidad:
            raise ErrorDatos(f"{contexto}: código duplicado con partida/unidad distinta: {codigo}")
        grupo["cantidad_decimal"] += cantidad
        grupo["planos"].add(plano)
    salida = []
    for grupo in por_codigo.values():
        cantidad = grupo["cantidad_decimal"].quantize(QTY, rounding=ROUND_HALF_UP)
        if cantidad <= 0:
            raise ErrorDatos(f"Metrado con cantidad redondeada a cero: {grupo['codigo']}")
        salida.append({"codigo": grupo["codigo"], "partida": grupo["partida"],
                       "unidad": grupo["unidad"], "cantidad": str(cantidad),
                       "referencias_planos": "; ".join(sorted(grupo["planos"]))})
    return salida


def precios_unitarios(filas: list[dict[str, str]]) -> dict[str, Decimal]:
    apu: dict[str, Decimal] = {}
    for i, fila in enumerate(filas, 2):
        ctx = f"APU fila {i}"
        codigo = campo(fila, "codigo", ctx)
        campo(fila, "recurso", ctx)
        campo(fila, "unidad_recurso", ctx)
        campo(fila, "fuente_precio", ctx)
        campo(fila, "fecha_precio", ctx)
        consumo = numero(fila.get("cantidad_por_unidad"), f"{ctx}.cantidad_por_unidad", estricto=True)
        precio = numero(fila.get("precio_recurso_pen"), f"{ctx}.precio_recurso_pen")
        apu[codigo] = apu.get(codigo, Decimal(0)) + consumo * precio
    return {codigo: valor.quantize(QTY, rounding=ROUND_HALF_UP) for codigo, valor in apu.items()}


def presupuesto(filas_metrado: list[dict[str, str]], filas_apu: list[dict[str, str]],
                gg: Decimal = Decimal(0), utilidad: Decimal = Decimal(0),
                igv: Decimal = Decimal(0)) -> tuple[list[dict[str, str]], dict[str, str]]:
    for nombre, valor in (("gastos_generales", gg), ("utilidad", utilidad), ("igv", igv)):
        if not valor.is_finite() or valor < 0 or valor > 100:
            raise ErrorDatos(f"{nombre}: porcentaje fuera de 0 a 100")
    cantidades = set()
    for fila in filas_metrado:
        codigo = campo(fila, "codigo", "Metrado consolidado")
        if codigo in cantidades:
            raise ErrorDatos(f"Código duplicado en metrado consolidado: {codigo}")
        cantidades.add(codigo)
    apu = precios_unitarios(filas_apu)
    if cantidades != set(apu):
        sin_apu = sorted(cantidades - set(apu))
        sin_metrado = sorted(set(apu) - cantidades)
        raise ErrorDatos(f"Códigos sin APU: {sin_apu}; códigos APU sin metrado: {sin_metrado}")
    salida = []
    directo = Decimal(0)
    for fila in filas_metrado:
        codigo = fila["codigo"]
        cantidad = numero(fila.get("cantidad"), f"cantidad {codigo}", estricto=True)
        precio = apu[codigo]
        parcial = (cantidad * precio).quantize(MONEY, rounding=ROUND_HALF_UP)
        directo += parcial
        salida.append({"codigo": codigo, "partida": campo(fila, "partida", codigo),
                       "unidad": campo(fila, "unidad", codigo),
                       "metrado": str(cantidad), "precio_unitario_pen": str(precio),
                       "parcial_pen": str(parcial)})
    general = (directo * gg / 100).quantize(MONEY, rounding=ROUND_HALF_UP)
    utilidad_pen = (directo * utilidad / 100).quantize(MONEY, rounding=ROUND_HALF_UP)
    subtotal = directo + general + utilidad_pen
    impuesto = (subtotal * igv / 100).quantize(MONEY, rounding=ROUND_HALF_UP)
    total = subtotal + impuesto
    resumen = {"moneda": "PEN", "partidas": len(salida), "costo_directo_pen": str(directo),
               "porcentaje_gastos_generales": str(gg), "gastos_generales_pen": str(general),
               "porcentaje_utilidad": str(utilidad), "utilidad_pen": str(utilidad_pen),
               "subtotal_pen": str(subtotal), "porcentaje_igv": str(igv),
               "igv_pen": str(impuesto), "presupuesto_total_pen": str(total),
               "advertencia": "Cálculo auxiliar, sujeto a validación técnica, económica y tributaria."}
    return salida, resumen


def guarda_csv(ruta: str | Path, campos: list[str], filas: list[dict[str, str]]) -> None:
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", encoding="utf-8", newline="") as fh:
        escritor = csv.DictWriter(fh, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(filas)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Metrados y presupuesto referencial de edificaciones en PEN")
    sub = parser.add_subparsers(dest="comando", required=True)
    pm = sub.add_parser("metrados", help="Consolidar geometrías y cantidades")
    pm.add_argument("--entrada", required=True)
    pm.add_argument("--salida", required=True)
    pp = sub.add_parser("presupuesto", help="Calcular APU, parciales y resumen")
    pp.add_argument("--metrados", required=True)
    pp.add_argument("--apu", required=True)
    pp.add_argument("--salida", required=True)
    pp.add_argument("--resumen", required=True)
    pp.add_argument("--gastos-generales", default="0", help="Porcentaje de costo directo")
    pp.add_argument("--utilidad", default="0", help="Porcentaje de costo directo")
    pp.add_argument("--igv", default="0", help="Porcentaje aplicable al subtotal")
    args = parser.parse_args(argv)
    try:
        if args.comando == "metrados":
            filas = metrados(lee_csv(args.entrada, CAMPOS_METRADO))
            guarda_csv(args.salida, SALIDA_METRADOS, filas)
            print(f"Metrados generados: {len(filas)} partidas -> {args.salida}")
        else:
            cantidades = lee_csv(args.metrados, SALIDA_METRADOS)
            recursos = lee_csv(args.apu, CAMPOS_APU)
            tasas = [numero(getattr(args, k), k) for k in ("gastos_generales", "utilidad", "igv")]
            filas, resumen = presupuesto(cantidades, recursos, *tasas)
            guarda_csv(args.salida, SALIDA_PRESUPUESTO, filas)
            destino = Path(args.resumen)
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_text(json.dumps(resumen, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"Presupuesto referencial S/ {resumen['presupuesto_total_pen']} -> {args.salida}")
        return 0
    except (ErrorDatos, OSError) as exc:
        parser.exit(2, f"ERROR: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
