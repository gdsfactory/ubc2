"""Sample mask for the edx course Q1 2023."""

from functools import partial
from pathlib import Path

import gdsfactory as gf
import ubcpdk
import ubcpdk.components as pdk
from gdsfactory.components.bend_circular import bend_circular
from gdsfactory.components.via_stack import via_stack_heater_m3
from ubcpdk.tech import LAYER, strip

from ubc2.write_mask import write_mask_gds_with_metadata

via_stack_heater_m3_mini = partial(via_stack_heater_m3, size=(4, 4))


size = (605, 440)
add_gc = ubcpdk.components.add_fiber_array
layer_label = LAYER.TEXT
GC_PITCH = 127


def test_mask1() -> Path:
    """Rings with different waveguide widths and gaps."""
    widths = [0.3, 0.4, 0.5]
    e = [
        add_gc(
            gf.add_tapers(
                ubcpdk.components.straight(
                    length=30, cross_section=gf.partial(strip, width=width)
                ),
                taper=gf.components.taper,
            ),
            component_name=f"straight_width_{width}",
        )
        for width in widths
    ]
    e += [
        add_gc(
            gf.add_tapers(
                pdk.ring_single(
                    radius=12,
                    gap=0.2,
                    length_x=0,
                    length_y=0,
                    bend=bend_circular,
                    bend_coupler=bend_circular,
                    cross_section=gf.partial(strip, width=width),
                    pass_cross_section_to_bend=True,
                ),
                taper=gf.components.taper,
            ),
            component_name=f"ring_width_{width}_gap_{gap}",
        )
        for width in widths
        for gap in [0.2, 0.3, 0.4]
    ]

    c = gf.pack(e)
    m = c[0]
    m.name = "EBeam_simbilod_1"
    _ = m << gf.components.rectangle(size=size, layer=LAYER.FLOORPLAN)
    return write_mask_gds_with_metadata(m)


if __name__ == "__main__":
    m = test_mask1()
    gf.show(m)
