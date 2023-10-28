"""Sample mask for the edx course Q1 2023."""

import itertools
from functools import partial
from pathlib import Path

import gdsfactory as gf
import ubcpdk
from gdsfactory.components.via_stack import via_stack_heater_m3
from gdsfactory.typings import Tuple
from ubcpdk.tech import LAYER

from ubc2.write_mask import size, write_mask_gds_with_metadata

via_stack_heater_m3_mini = partial(via_stack_heater_m3, size=(4, 4))

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
        width=0.061,
        layer=LAYER.WG,
        offset=-(slab_width / 2 + gap + width / 2),
        name="continuum",
    )
    s2 = gf.Section(
        width=slab_width,
        layer=LAYER.WG,
        offset=-(slab_width / 2 + gap + width / 2),
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
    gaps: Tuple[float] = (0.15,),
    widths: Tuple[float] = (0.5,),
    lengths: Tuple[float] = (
        0.001,
        50,
        100,
        150,
        200,
    ),
    slab_width: float = 25,
    name: str = "EBeam_simbilod_10",
) -> Path:
    """Slab of silicon close to a waveguide."""

    # Test structure w/ local loss calibration
    e = []
    for gap, width in itertools.product(gaps, widths):
        e += [
            add_gc(
                continuum_coupling(
                    gap=gap, width=width, length=length, slab_width=slab_width
                ),
                with_loopback=True,
                component_name=f"continuum_gap_{gap:1.3f}_width_{width:1.3f}_length_{length:1.3f}",
                fanout_length=30,
                optical_routing_type=1,
            )
            for length in lengths
        ]

    c = gf.pack(e)
    m = c[0]
    m.name = name
    _ = m << gf.components.rectangle(size=size, layer=LAYER.FLOORPLAN)
    return write_mask_gds_with_metadata(m)


test_mask_continuum1 = gf.partial(test_mask_continuum, name="EBeam_simbilod_10")
test_mask_continuum2 = gf.partial(
    test_mask_continuum, gaps=(0.2,), name="EBeam_simbilod_11"
)
test_mask_continuum3 = gf.partial(
    test_mask_continuum, gaps=(0.25,), name="EBeam_simbilod_12"
)

if __name__ == "__main__":
    # m = test_mask_rings_1()
    # m = test_mask_rings_2()
    m = test_mask_continuum2()
    gf.show(m)
