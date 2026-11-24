# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.triggers import Timer


@cocotb.test()
async def test_project(dut):
    dut.clk.value = 0
    dut.rst_n.value = 1
    dut.ena.value = 1

    # Cada caso contiene A, B y el resultado esperado en ocho bits.
    casos = [
        (0, 0, 0),
        (20, 30, 50),
        (127, 1, 128),
        (255, 1, 0),
        (255, 255, 254),
    ]

    for a, b, esperado in casos:
        dut.ui_in.value = a
        dut.uio_in.value = b

        await Timer(100, unit="ns")

        obtenido = int(dut.uo_out.value)
        assert obtenido == esperado, (
            f"A={a}, B={b}: se esperaba {esperado}, se obtuvo {obtenido}"
        )
