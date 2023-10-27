"""Sample mask for the edx course Q1 2023."""

from functools import partial
from pathlib import Path

import gdsfactory as gf
import ubcpdk
from gdsfactory.components.bend_circular import bend_circular
from gdsfactory.components.bend_euler import bend_euler
from gdsfactory.components.via_stack import via_stack_heater_m3
from gdsfactory.typings import Tuple
from ubcpdk.tech import LAYER

from ubc2.write_mask import size, write_mask_gds_with_metadata

via_stack_heater_m3_mini = partial(via_stack_heater_m3, size=(4, 4))

add_gc = ubcpdk.components.add_fiber_array
layer_label = LAYER.TEXT
GC_PITCH = 127


radii = (2, 4, 6)
columns = (10, 7, 5)
rows = (3, 5, 8)


def test_mask_bends_circular(
    radii: Tuple[float] = radii,
    columns: Tuple[float] = columns,
    rows: Tuple[float] = rows,
    name: str = "EBeam_simbilod_20",
) -> Path:
    """Bend cutbacks."""

    # Test structure w/ local loss calibration
    e = []
    for radius, column, row in zip(radii, columns, rows):
        c = gf.components.cutback_bend90circular(
            straight_length=1.0,
            rows=row,
            columns=column,
            spacing=5,
            bend90=gf.partial(bend_circular, radius=radius),
        )
        num_bends = c.info["n_bends"]

        e += [
            add_gc(
                c,
                name=f"bends_circular_radius_{radius:1.3f}_nbends_{num_bends}",
                optical_routing_type=2,
                fanout_length=1,
                with_loopback=True,
            )
        ]

    c = gf.pack(e)
    m = c[0]
    m.name = name
    _ = m << gf.components.rectangle(size=size, layer=LAYER.FLOORPLAN)
    return write_mask_gds_with_metadata(m)


def test_mask_bends_euler(
    radii: Tuple[float] = radii,
    columns: Tuple[float] = columns,
    rows: Tuple[float] = rows,
    name: str = "EBeam_simbilod_21",
) -> Path:
    """Bend cutbacks."""

    # Test structure w/ local loss calibration
    e = []
    for radius, column, row in zip(radii, columns, rows):
        c = gf.components.cutback_bend90(
            straight_length=1.0,
            rows=row,
            columns=column,
            spacing=5,
            bend90=gf.partial(bend_euler, radius=radius),
        )
        num_bends = c.info["n_bends"]

        e += [
            add_gc(
                c,
                name=f"bends_euler_radius_{radius:1.3f}_nbends_{num_bends}",
                optical_routing_type=2,
                with_loopback=True,
                fanout_length=1,
            )
        ]

        print(f"Radius: {radius}, number of bends: {num_bends}")

    c = gf.pack(e)
    m = c[0]
    m.name = name
    _ = m << gf.components.rectangle(size=size, layer=LAYER.FLOORPLAN)
    return write_mask_gds_with_metadata(m)


if __name__ == "__main__":
    # m = test_mask_bends_circular()
    m = test_mask_bends_euler()
    gf.show(m)
