"""Sample mask for the edx course Q1 2023."""

from pathlib import Path

import gdsfactory as gf
import ubcpdk
import ubcpdk.components as pdk
from ubcpdk import tech
from ubcpdk.tech import LAYER

from ubc2.cutback_2x2 import cutback_2x2
from ubc2.write_mask import (
    add_gc,
    pack,
    size,
    write_mask_gds_with_metadata,
)

length_x = 0.1


def test_mask1() -> Path:
    """Add DBR cavities."""
    e = [add_gc(pdk.mzi(delta_length=dl)) for dl in [9.32, 93.19]]
    e += [
        add_gc(pdk.ring_single(radius=12, gap=gap, length_x=coupling_length))
        for gap in [0.2]
        for coupling_length in [0.1, 2.5]
    ]

    e += [
        ubcpdk.components.dbr_cavity_te(w0=w0, dw=dw)
        for w0 in [0.5]
        for dw in [50e-3, 100e-3, 150e-3, 200e-3]
    ]
    e += [add_gc(ubcpdk.components.ring_with_crossing())]
    e += [
        add_gc(
            ubcpdk.components.ring_with_crossing(port_name="o2", with_component=False)
        )
    ]

    c = pack(e)
    m = c[0]
    if len(c) > 1:
        raise ValueError(f"Failed to pack. It requires {len(c)}")
    m.name = "EBeam_JoaquinMatres_11"
    _ = m << gf.components.rectangle(size=size, layer=LAYER.FLOORPLAN)
    return write_mask_gds_with_metadata(m)


def test_mask2() -> Path:
    """spirals for extracting straight waveguide loss"""
    N = 11
    radius = 5

    e = [
        ubcpdk.components.add_fiber_array(
            optical_routing_type=1,
            component=ubcpdk.components.spiral(
                N=N,
                radius=radius,
                y_straight_inner_top=0,
                x_inner_length_cutback=0,
                info=dict(does=["spiral", "te1550"]),
            ),
        )
    ]

    e.append(
        ubcpdk.components.add_fiber_array(
            optical_routing_type=1,
            component=ubcpdk.components.spiral(
                N=N,
                radius=radius,
                y_straight_inner_top=0,
                x_inner_length_cutback=150,
            ),
        )
    )

    c = pack(e)

    m = c[0]
    m.name = "EBeam_JoaquinMatres_12"
    _ = m << gf.components.rectangle(size=size, layer=LAYER.FLOORPLAN)
    return write_mask_gds_with_metadata(m)


def test_mask3() -> Path:
    """contains mirror cavities and structures inside a resonator"""
    e = []
    e += [add_gc(ubcpdk.components.ebeam_crossing4())]
    e += [add_gc(ubcpdk.components.ebeam_adiabatic_te1550(), optical_routing_type=1)]
    e += [add_gc(ubcpdk.components.ebeam_bdc_te1550())]
    e += [add_gc(ubcpdk.components.ebeam_y_1550(), optical_routing_type=1)]
    e += [add_gc(ubcpdk.components.ebeam_y_adiabatic_tapers(), optical_routing_type=1)]
    e += [
        add_gc(ubcpdk.components.straight(), component_name=f"straight_{i}")
        for i in range(2)
    ]
    c = pack(e)
    m = c[0]
    m.name = "EBeam_JoaquinMatres_13"
    _ = m << gf.components.rectangle(size=size, layer=LAYER.FLOORPLAN)
    return write_mask_gds_with_metadata(m)


def test_mask4() -> Path:
    """Ring resonators Radius 10um."""
    gaps = [50, 100, 150, 200]
    radiuses = [10]

    rings = [
        pdk.ring_double(
            radius=radius, length_x=length_x, gap=gap * 1e-3, decorator=add_gc
        )
        for radius in radiuses
        for gap in gaps
    ]
    gaps = [100, 150]
    radiuses = [3]
    rings += [
        pdk.ring_double(
            radius=radius, length_x=length_x, gap=gap * 1e-3, decorator=add_gc
        )
        for radius in radiuses
        for gap in gaps
    ]

    c = pack(rings)
    m = c[0]
    m.name = "EBeam_JoaquinMatres_14"
    _ = m << gf.components.rectangle(size=size, layer=LAYER.FLOORPLAN)
    return write_mask_gds_with_metadata(m)


def test_mask5() -> Path:
    """Ring resonators."""
    e = []
    e += [
        pdk.dbr_cavity_te(dw=dw * 1e-3, n=350)
        for dw in [5, 10, 20, 40, 60, 80, 100, 150, 200]
    ]

    c = pack(e)
    m = c[0]
    m.name = "EBeam_JoaquinMatres_15"
    _ = m << gf.components.rectangle(size=size, layer=LAYER.FLOORPLAN)
    return write_mask_gds_with_metadata(m)


def test_mask6() -> Path:
    """Splitters 1x2."""
    mmis = []
    mmis += [
        gf.components.cutback_splitter(
            component=pdk.ebeam_y_adiabatic_tapers,
            cols=1,
            rows=7,
            bend180=pdk.bend_euler180_sc,
        )
    ]
    mmis += [
        gf.components.cutback_splitter(
            component=pdk.ebeam_y_1550, cols=4, rows=7, bend180=pdk.bend_euler180_sc
        )
    ]
    mmis_gc = [pdk.add_fiber_array(mmi, optical_routing_type=1) for mmi in mmis]

    c = pack(mmis_gc)
    m = c[0]
    m.name = "EBeam_JoaquinMatres_16"
    _ = m << gf.components.rectangle(size=size, layer=LAYER.FLOORPLAN)
    return write_mask_gds_with_metadata(m)


def test_mask7() -> Path:
    """Splitters 2x2."""
    # mmi2x2_with_sbend = partial(
    #     gf.components.mmi2x2_with_sbend,
    #     decorator=tech.add_pins_bbox_siepic_remove_layers,
    # )

    mmi2x2_with_sbend = tech.add_pins_bbox_siepic_remove_layers(
        gf.components.mmi2x2_with_sbend().flatten()
    )
    mmi2x2_with_sbend.name = "mmi2x2_with_sbend"

    mmis = []
    mmis += [cutback_2x2(component=pdk.ebeam_bdc_te1550, cols=2)]
    mmis += [cutback_2x2(component=mmi2x2_with_sbend, cols=4)]

    mmis += [mmi2x2_with_sbend]
    mmis += [pdk.ebeam_bdc_te1550()]

    mmis_gc = [
        pdk.add_fiber_array(component=mmi, optical_routing_type=1) for mmi in mmis
    ]
    c = pack(mmis_gc)

    m = c[0]
    if len(c) > 1:
        raise ValueError(f"Failed to pack. It requires {len(c)}")
    m.name = "EBeam_JoaquinMatres_17"
    _ = m << gf.components.rectangle(size=size, layer=LAYER.FLOORPLAN)
    return write_mask_gds_with_metadata(m)


if __name__ == "__main__":
    # c = test_mask1()  # dbr and mzi
    # c = test_mask2()  # spirals
    # c = test_mask3()  # coupler and crossing
    # c = test_mask4()  # rings
    c = test_mask5()  # dbr cavity
    # c = test_mask6()  # 1x2 mmis
    # c = test_mask7()  # 2x2mmis
    gf.show(c)
    # c = partial(
    #     gf.components.mmi2x2_with_sbend,
    #     decorator=tech.add_pins_bbox_siepic_remove_layers,
    # )()
    # c.show()
