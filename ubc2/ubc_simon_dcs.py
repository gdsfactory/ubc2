"""Sample mask for the edx course Q1 2023."""

from functools import partial
from pathlib import Path

import gdsfactory as gf
import ubcpdk
from gdsfactory.component import Component
from gdsfactory.components import bend_s
from gdsfactory.components.via_stack import via_stack_heater_m3
from gdsfactory.typings import CrossSectionSpec
from ubcpdk.tech import LAYER

from ubc2.write_mask import size, write_mask_gds_with_metadata

via_stack_heater_m3_mini = partial(via_stack_heater_m3, size=(4, 4))

add_gc = ubcpdk.components.add_fiber_array
layer_label = LAYER.TEXT
GC_PITCH = 127


@gf.cell
def coupler_asymmetric_full(
    coupling_length: float = 40.0,
    dx: float = 10.0,
    dy: float = 4.8,
    gap: float = 0.1,
    width_top: float = 0.45,
    width_bot: float = 0.5,
    cross_section: CrossSectionSpec = "xs_sc",
    **kwargs,
) -> Component:
    c = gf.Component()

    x = gf.get_cross_section(cross_section=cross_section, **kwargs)

    x_top = x.copy(width=width_top)
    x_bottom = x.copy(width=width_bot)

    coupler = c << gf.components.coupler_straight_asymmetric(
        length=coupling_length,
        gap=gap,
        width_top=width_top,
        width_bot=width_bot,
    )

    bend_input_top = (
        c
        << bend_s(
            size=(dx, (dy - gap - x_top.width) / 2.0), cross_section=x_top
        ).mirror()
    )
    bend_input_bottom = (
        c
        << bend_s(
            size=(dx, (-dy + gap + x_bottom.width) / 2.0), cross_section=x_bottom
        ).mirror()
    )
    bend_output_top = (
        c
        << bend_s(
            size=(dx, (dy - gap - x_top.width) / 2.0), cross_section=x_bottom
        ).mirror()
    )
    bend_output_bottom = (
        c
        << bend_s(
            size=(dx, (-dy + gap + x_bottom.width) / 2.0), cross_section=x_top
        ).mirror()
    )

    bend_input_top.connect("o1", coupler.ports["o2"])
    bend_input_bottom.connect("o1", coupler.ports["o1"])
    bend_output_top.connect("o2", coupler.ports["o4"])
    bend_output_bottom.connect("o2", coupler.ports["o3"])

    c.absorb(bend_input_bottom)
    c.absorb(bend_input_top)
    c.absorb(bend_output_top)
    c.absorb(bend_output_bottom)
    c.absorb(coupler)

    if x.add_bbox:
        c = x.add_bbox(c)

    if x.info:
        c.info = x.info

    c.add_port("o1", port=bend_input_bottom.ports["o2"])
    c.add_port("o2", port=bend_input_top.ports["o2"])
    c.add_port("o3", port=bend_output_top.ports["o1"])
    c.add_port("o4", port=bend_output_bottom.ports["o1"])

    c.auto_rename_ports()

    return c


def test_mask_dcs(
    width_top: float = 0.45,
    width_bot: float = 0.5,
    lengths: float = (0, 2, 4, 6, 8, 10, 12, 14),
    gap: float = 0.1,
    name: str = "EBeam_simbilod_40",
) -> Path:
    """Directional couplers with different width deltas and lengths."""

    e = []

    e += [
        add_gc(
            gf.add_tapers(
                coupler_asymmetric_full(
                    coupling_length=length,
                    gap=gap,
                    width_top=width_top,
                    width_bot=width_bot,
                ),
                taper=gf.components.taper,
            ),
            component_name=f"dc_width1_{width_top:1.3f}_width2_{width_bot:1.3f}_length_{length:1.3f}_gap_{gap:1.3f}",
        )
        for length in lengths
    ]

    c = gf.pack(e)
    m = c[0]
    m.name = name
    _ = m << gf.components.rectangle(size=size, layer=LAYER.FLOORPLAN)
    return write_mask_gds_with_metadata(m)


test_mask_dcs_1 = gf.partial(test_mask_dcs, name="EBeam_simbilod_40")
test_mask_dcs_2 = gf.partial(
    test_mask_dcs, lengths=(1, 3, 5, 7, 9, 11, 13, 15), name="EBeam_simbilod_41"
)

test_mask_dcs_3 = gf.partial(
    test_mask_dcs, width_top=0.4, width_bot=0.35, name="EBeam_simbilod_42"
)
test_mask_dcs_4 = gf.partial(
    test_mask_dcs,
    width_top=0.4,
    width_bot=0.35,
    lengths=(1, 3, 5, 7, 9, 11, 13, 15),
    name="EBeam_simbilod_43",
)
test_mask_dcs_5 = gf.partial(
    test_mask_dcs, width_top=0.4, width_bot=0.35, gap=0.2, name="EBeam_simbilod_44"
)
test_mask_dcs_6 = gf.partial(
    test_mask_dcs,
    width_top=0.4,
    width_bot=0.35,
    gap=0.2,
    lengths=(1, 3, 5, 7, 9, 11, 13, 15),
    name="EBeam_simbilod_45",
)


if __name__ == "__main__":
    m = test_mask_dcs()
    # m = coupler_asymmetric_full()
    gf.show(m, show_ports=True)
