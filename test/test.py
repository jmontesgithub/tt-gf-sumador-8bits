# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0
#
# Test para tt_um_8bitadder (Ripple Carry Adder de 8 bits)
#   ui_in[7:0]  -> A
#   uio_in[7:0] -> B
#   uo_out[7:0] -> (A + B) mod 256   (el acarreo final no sale del chip)
#   uio_out / uio_oe -> siempre 0 (los pines uio son entradas)

import os
import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, Timer

# El sumador es combinacional: basta con esperar a que se propague el acarreo.
# 100 ns deja margen de sobra para la simulación de compuertas (UNIT_DELAY=#1).
SETTLE_NS = 100


def expected(a: int, b: int) -> int:
    return (a + b) & 0xFF


async def apply_and_check(dut, a: int, b: int):
    dut.ui_in.value = a
    dut.uio_in.value = b
    await Timer(SETTLE_NS, unit="ns")
    got = int(dut.uo_out.value)
    exp = expected(a, b)
    assert got == exp, f"{a} + {b}: esperado {exp}, obtenido {got}"


async def reset(dut):
    """Arranca reloj y reset (el diseño no los usa, pero así lo hace el chip real)."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="us").start())
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1


@cocotb.test()
async def test_uio_are_inputs(dut):
    """Los pines uio deben quedar como entradas (uio_oe = 0) y uio_out = 0."""
    await reset(dut)
    for b in (0x00, 0xFF, 0xA5):
        dut.uio_in.value = b
        await Timer(SETTLE_NS, unit="ns")
        assert int(dut.uio_oe.value) == 0, f"uio_oe = {dut.uio_oe.value}, debe ser 0"
        assert int(dut.uio_out.value) == 0, f"uio_out = {dut.uio_out.value}, debe ser 0"


@cocotb.test()
async def test_directed(dut):
    """Casos dirigidos: ceros, propagación de acarreo y overflow."""
    await reset(dut)
    cases = [
        (20, 30),     # ejemplo de la plantilla -> 50
        (0, 0),
        (1, 1),
        (15, 1),      # acarreo del nibble bajo al alto (0x0F + 1 = 0x10)
        (127, 1),     # acarreo hasta el MSB (0x7F + 1 = 0x80)
        (127, 127),   # 254
        (255, 1),     # acarreo que recorre los 8 bits -> 0 (overflow)
        (255, 255),   # 510 mod 256 = 254
        (0xAA, 0x55), # bits alternados, sin acarreos -> 255
        (128, 128),   # solo se desborda el MSB -> 0
    ]
    for a, b in cases:
        await apply_and_check(dut, a, b)
        dut._log.info(f"{a:3d} + {b:3d} = {int(dut.uo_out.value):3d}  OK")


@cocotb.test()
async def test_bit_by_bit(dut):
    """Cada sumador completo por separado: A = 2^i con B = 0, y luego B = 2^i."""
    await reset(dut)
    for i in range(8):
        await apply_and_check(dut, 1 << i, 0)
        await apply_and_check(dut, 0, 1 << i)
        await apply_and_check(dut, 1 << i, 1 << i)  # fuerza acarreo al bit i+1


@cocotb.test()
async def test_exhaustive(dut):
    """Todas las combinaciones A,B (65 536).

    En simulación de compuertas (GATES=yes) es más lento; se puede limitar con
    la variable de entorno ADDER_SAMPLES=<n> para probar n pares aleatorios.
    """
    await reset(dut)
    samples = os.environ.get("ADDER_SAMPLES")
    if samples:
        rng = random.Random(1234)
        pairs = [(rng.randrange(256), rng.randrange(256)) for _ in range(int(samples))]
    else:
        pairs = [(a, b) for a in range(256) for b in range(256)]

    for a, b in pairs:
        await apply_and_check(dut, a, b)
    dut._log.info(f"{len(pairs)} combinaciones verificadas")
