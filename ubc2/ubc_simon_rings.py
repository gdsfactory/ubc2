"""Sample mask for the edx course Q1 2023."""

from functools import partial
from pathlib import Path

import gdsfactory as gf
import ubcpdk
import ubcpdk.components as pdk
from gdsfactory.components.bend_circular import bend_circular
from gdsfactory.components.via_stack import via_stack_heater_m3
from gdsfactory.typings import Tuple
from ubcpdk.tech import LAYER, strip

from ubc2.write_mask import write_mask_gds_with_metadata

via_stack_heater_m3_mini = partial(via_stack_heater_m3, size=(4, 4))


size = (605, 440)
add_gc = ubcpdk.components.add_fiber_array
layer_label = LAYER.TEXT
GC_PITCH = 127


def test_mask_rings(
    widths: Tuple[float] = (0.3, 0.4, 0.5),
    gaps: Tuple[float] = (0.2, 0.3, 0.4),
    radii: Tuple[float] = (12,),
    name: str = "EBeam_simbilod_1",
) -> Path:
    """Rings with different waveguide widths and gaps."""

    e = [
        add_gc(
            gf.add_tapers(
                ubcpdk.components.straight(
                    length=2 * (radius + 3),
                    cross_section=gf.partial(
                        strip, width=width
                    ),  # 3 is default ring_coupler length extension
                ),
                taper=gf.components.taper,
            ),
            component_name=f"straight_width_{width:1.3f}",
        )
        for width in widths
        for radius in radii
    ]
    e += [
        add_gc(
            gf.add_tapers(
                pdk.ring_single(
                    radius=radius,
                    gap=gap,
                    length_x=0,
                    length_y=0,
                    bend=bend_circular,
                    bend_coupler=bend_circular,
                    cross_section=gf.partial(strip, width=width),
                    pass_cross_section_to_bend=True,
                ),
                taper=gf.components.taper,
            ),
            component_name=f"ring_width_{width:1.3f}_gap_{gap:1.3f}_radius_{radius:1.3f}",
        )
        for width in widths
        for gap in gaps
        for radius in radii
    ]

    c = gf.pack(e)
    m = c[0]
    m.name = name
    _ = m << gf.components.rectangle(size=size, layer=LAYER.FLOORPLAN)
    return write_mask_gds_with_metadata(m)


test_mask_rings_1 = gf.partial(test_mask_rings)
test_mask_rings_2 = gf.partial(
    test_mask_rings, gaps=(0.25, 0.35, 0.45), name="EBeam_simbilod_2"
)
test_mask_rings_3 = gf.partial(
    test_mask_rings,
    gaps=(0.25, 0.35, 0.45),
    widths=(0.5,),
    radii=(
        5,
        8,
    ),
    name="EBeam_simbilod_3",
)

if __name__ == "__main__":
    # m = test_mask_rings_1()
    # m = test_mask_rings_2()
    m = test_mask_rings_3()
    gf.show(m)
