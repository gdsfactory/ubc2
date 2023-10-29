"""Sample mask for the edx course Q1 2023."""

from functools import partial
from pathlib import Path

import gdsfactory as gf
import ubcpdk
import ubcpdk.components as pdk
from ubcpdk.tech import LAYER

from ubc2.write_mask import (
    add_gc,
    pack_actives,
    size_actives,
    write_mask_gds_with_metadata,
)


def test_mzi_heater() -> Path:
    """Heated MZI interferometers."""
    mzi = partial(gf.components.mzi, splitter=ubcpdk.components.ebeam_y_1550)
    mzis = [mzi(delta_length=delta_length) for delta_length in [10, 40, 100]]
    mzis_gc = [pdk.add_fiber_array(mzi) for mzi in mzis]

    mzis = [pdk.mzi_heater(delta_length=delta_length) for delta_length in [40]]
    mzis_heater_gc = [
        pdk.add_fiber_array_pads_rf(mzi, orientation=90, optical_routing_type=2)
        for mzi in mzis
    ]

    c = pack_actives(mzis_gc + mzis_heater_gc)
    m = c[0]
    m.name = "EBeam_heaters_JoaquinMatres_14"
    _ = m << gf.components.rectangle(size=size_actives, layer=LAYER.FLOORPLAN)
    return write_mask_gds_with_metadata(m)


def test_ring_heater() -> Path:
    """Heated Ring resonators."""
    lengths_x = [0.2]
    gaps = [0.2]

    rings = [
        pdk.ring_double_heater(radius=12, length_x=length_x, gap=gap)
        for length_x in lengths_x
        for gap in gaps
    ]
    rings = [gf.functions.rotate180(ring) for ring in rings]
    rings_gc = [pdk.add_fiber_array_pads_rf(ring) for ring in rings]
    rings_gc += [
        add_gc(pdk.ring_double(radius=12, gap=gap, length_x=length_x))
        for gap in gaps
        for length_x in lengths_x
    ]

    c = pack_actives(rings_gc)
    m = c[0]
    m.name = "EBeam_heaters_JoaquinMatres_15"
    _ = m << gf.components.rectangle(size=size_actives, layer=LAYER.FLOORPLAN)
    return write_mask_gds_with_metadata(m)


if __name__ == "__main__":
    c = test_ring_heater()
    gf.show(c)
