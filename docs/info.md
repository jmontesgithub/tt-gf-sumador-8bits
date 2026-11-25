<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

This project is an 8-bit ripple carry adder built from eight full adders, each made of two half adders.
The carry output of each stage feeds the carry input of the next one.

- `ui_in[7:0]` is operand **A**.
- `uio_in[7:0]` is operand **B** (all `uio` pins are configured as inputs).
- `uo_out[7:0]` shows **SUM = (A + B) mod 256**. The final carry-out is not connected to a pin.

The design is purely combinational: the clock and reset are not used.

## How to test

Set A with the 8 input switches (`ui_in`) and B on the bidirectional pins (`uio_in`).
The sum appears immediately on the outputs (`uo_out`). Examples:

| A   | B   | SUM |
|-----|-----|-----|
| 20  | 30  | 50  |
| 15  | 1   | 16  |
| 255 | 1   | 0   |
| 255 | 255 | 254 |

The cocotb testbench in `test/test.py` checks the `uio` pin configuration, directed carry and overflow cases,
each full adder bit by bit, and all 65,536 input combinations.

## External hardware

None. Only the input switches and the output LEDs / 7-segment display of the Tiny Tapeout demo board are needed.
