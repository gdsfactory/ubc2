"""Sample mask for the edx course Q1 2023."""

import itertools
from functools import partial
from pathlib import Path

import gdsfactory as gf
import ubcpdk
from gdsfactory.components.via_stack import via_stack_heater_m3
from gdsfactory.typings import Tuple
from ubcpdk.tech import LAYER

via_stack_heater_m3_mini = partial(via_stack_heater_m3, size=(4, 4))


size = (605, 440)
add_gc = ubcpdk.components.add_fiber_array
layer_label = LAYER.TEXT
GC_PITCH = 127


@gf.cell
def continuum_coupling(
    gap: float = 0.5,
    width: float = 0.5,
    length: float = 100,
    slab_width: float = 30,
    taper_length: float = 50,
):
    c = gf.Component()

    s0 = gf.Section(
        width=width,
        layer=LAYER.WG,
        name="waveguide",
        port_names=("o1", "o2"),
        port_types=("optical", "optical"),
    )
    s1 = gf.Section(
        width=width,
        layer=LAYER.WG,
        offset=slab_width / 2 + gap + width / 2,
        name="continuum",
    )
    s2 = gf.Section(
        width=slab_width,
        layer=LAYER.WG,
        offset=slab_width / 2 + gap + width / 2,
        name="continuum",
    )

    xs1 = gf.CrossSection(sections=[s0, s1])
    xs2 = gf.CrossSection(sections=[s0, s2])
    Xtrans = gf.path.transition(
        cross_section1=xs1, cross_section2=xs2, width_type="sine"
    )

    P1 = gf.path.straight(length=5)
    P2 = gf.path.straight(length=length)
    wg1 = gf.path.extrude(P1, xs1)
    wg2 = gf.path.extrude(P2, xs2)

    P3 = gf.path.straight(length=taper_length, npoints=100)
    straight_transition = gf.path.extrude_transition(P3, Xtrans)

    wg1ref = c << wg1
    wgtref = c << straight_transition
    wg2ref = c << wg2
    wgtref2 = c << straight_transition
    wgtref2.mirror_y()
    wg3ref = c << wg1
    wg3ref.mirror_y()

    wgtref.connect("o1", wg1ref.ports["o2"])
    wg2ref.connect("o1", wgtref.ports["o2"])
    wgtref2.connect("o2", wg2ref.ports["o2"])
    wg3ref.connect("o2", wgtref2.ports["o1"])

    c.add_port("o1", port=wg1ref.ports["o1"])
    c.add_port("o2", port=wg3ref.ports["o1"])

    return c


def test_mask_continuum(
    gaps: Tuple[float] = (0.2, 0.3, 0.4),
    widths: Tuple[float] = (0.5,),
    lengths: Tuple[float] = (100,),
    slab_width: float = 30,
    name: str = "EBeam_simbilod_1",
) -> Path:
    """Slab of silicon close to a waveguide."""

    # Deembedding structure
    [
        add_gc(ubcpdk.components.straight(), component_name=f"straight_{i}")
        for i in range(1)
    ]

    # Test structure
    for gap, width in itertools.product(gaps, widths):
        s0 = gf.Section(
            width=width,
            layer=LAYER.WG,
            name="waveguide",
        )
        s1 = gf.Section(
            width=slab_width,
            layer=LAYER.WG,
            offset=slab_width / 2 + gap + width / 2,
            name="continuum",
        )

        xs1 = gf.partial(sections=[s0])
        xs1 = gf.partial(sections=[s0, s1])
        gf.path.transition(cross_section1=xs1, cross_section2=xs1, width_type="sine")

    # e += [
    #     add_gc(
    #         gf.add_tapers(
    #             pdk.ring_single(
    #                 radius=radius,
    #                 gap=gap,
    #                 length_x=0,
    #                 length_y=0,
    #                 bend=bend_circular,
    #                 bend_coupler=bend_circular,
    #                 cross_section=gf.partial(strip, width=width),
    #                 pass_cross_section_to_bend=True,
    #             ),
    #             taper=gf.components.taper,
    #         ),
    #         component_name=f"ring_width_{width:1.3f}_gap_{gap:1.3f}_radius_{radius:1.3f}",
    #     )
    #     for width in widths
    #     for gap in gaps
    #     for radius in radii
    # ]

    # c = gf.pack(e)
    # m = c[0]
    # m.name = name
    # _ = m << gf.components.rectangle(size=size, layer=LAYER.FLOORPLAN)
    # return write_mask_gds_with_metadata(m)


if __name__ == "__main__":
    # m = test_mask_rings_1()
    # m = test_mask_rings_2()
    m = continuum_coupling()
    gf.show(m)
