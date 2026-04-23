"""Sample mask for the edx course Q1 2023."""

from functools import partial
from pathlib import Path

import gdsfactory as gf
import ubcpdk
import ubcpdk.components as pdk
from gdsfactory.components.via_stack import via_stack_heater_m3
from ubcpdk.tech import LAYER

from ubc2.write_mask import size_actives, write_mask_gds_with_metadata

via_stack_heater_m3_mini = partial(via_stack_heater_m3, size=(4, 4))

add_gc = ubcpdk.components.add_fiber_array
layer_label = LAYER.TEXT
GC_PITCH = 127


@gf.cell
def small_delay(dx: float = 10):
    bend = gf.components.bend_euler()
    bend180 = gf.components.bend_euler180()
    straight = gf.components.straight(length=dx)

    gf.components.straight(length=dx)

    symbol_to_component = {
        "B": (straight, "o1", "o2"),
        "C": (bend180, "o1", "o2"),
        "A": (bend, "o2", "o1"),
    }

    sequence = "ABCBA"

    return gf.components.component_sequence(
        sequence=sequence, symbol_to_component=symbol_to_component
    )


@gf.cell
def mzi_xtalk(
    length_unheated: float = 50,
    gap: float = 5,
    waveguide_width: float = 0.5,
    length_heater: float = 100,
    delta_length: float = 40,
):
    c = gf.Component()

    # Splitter
    splitter = c << gf.components.mmi2x2_with_sbend()

    # Cross sections
    s0 = gf.Section(
        width=0.5, offset=0, layer=LAYER.WG, name="core", port_names=("o1", "o2")
    )
    regular_xs = gf.CrossSection(sections=[s0])
    s1 = gf.Section(
        width=waveguide_width,
        offset=0,
        layer=LAYER.WG,
        name="core",
        port_names=("o1", "o2"),
    )
    experiment_xs = gf.CrossSection(sections=[s1])
    transition_xs = gf.path.transition(
        cross_section1=regular_xs, cross_section2=experiment_xs, width_type="sine"
    )
    transition_xs_reversed = gf.path.transition(
        cross_section1=experiment_xs, cross_section2=regular_xs, width_type="sine"
    )

    # Bring waveguides within some distance, transitioning width
    base_distance = splitter.ports["o3"].y - splitter.ports["o4"].y
    distance = gap - base_distance

    spacer_top_left = c << gf.components.bend_s(
        size=(length_unheated, -distance / 2), cross_section=transition_xs
    )
    spacer_top_left.mirror()
    spacer_top_left.connect("o1", destination=splitter.ports["o3"])

    spacer_bot_left = c << gf.components.bend_s(
        size=(length_unheated, distance / 2), cross_section=transition_xs
    )
    spacer_bot_left.mirror()
    spacer_bot_left.connect("o1", destination=splitter.ports["o4"])

    #  Heating region
    heater_xs = gf.partial(ubcpdk.tech.strip_heater_metal, width=waveguide_width)
    heater_top = c << gf.components.straight_heater_metal(
        length=length_heater,
        cross_section=experiment_xs,
        cross_section_waveguide_heater=heater_xs,
    )
    heater_top.connect("o1", destination=spacer_top_left.ports["o2"])

    straight_bottom = c << gf.components.straight(
        length=length_heater, cross_section=experiment_xs
    )
    straight_bottom.connect("o1", destination=spacer_bot_left.ports["o2"])

    # Reverse
    spacer_top_right = c << gf.components.bend_s(
        size=(length_unheated, distance / 2), cross_section=transition_xs_reversed
    )
    spacer_top_right.mirror()
    spacer_top_right.connect("o1", destination=heater_top.ports["o2"])

    spacer_bot_right = c << gf.components.bend_s(
        size=(length_unheated, -distance / 2), cross_section=transition_xs_reversed
    )
    spacer_bot_right.mirror()
    spacer_bot_right.connect("o1", destination=straight_bottom.ports["o2"])

    # Custom delay lines
    length_top = 10
    length_bottom = length_top + delta_length

    top_delay = c << small_delay(dx=length_top / 2)
    top_delay.mirror()
    top_delay.connect("o1", destination=spacer_top_right.ports["o2"])
    bottom_delay = c << small_delay(dx=length_bottom / 2)
    bottom_delay.connect("o1", destination=spacer_bot_right.ports["o2"])

    combiner = c << gf.components.mmi2x2_with_sbend()
    combiner.connect("o1", destination=bottom_delay.ports["o2"])

    c.add_port("o1", port=splitter.ports["o1"])
    c.add_port("o2", port=splitter.ports["o2"])
    c.add_port("o3", port=combiner.ports["o3"])
    c.add_port("o4", port=combiner.ports["o4"])

    c.add_port("e_l", port=heater_top.ports["l_e4"])
    c.add_port("e_r", port=heater_top.ports["r_e2"])

    c.auto_rename_ports()

    return c


def test_mask_heating(
    gap: float = 2,
    width: float = 0.5,
    name: str = "EBeam_heaters_simbilod_50",
) -> Path:
    m = gf.Component()
    floorplan = m << gf.components.rectangle(size=size_actives, layer=LAYER.FLOORPLAN)

    # Pads
    pad_spacing = 125 - (pdk.pad().ymax - pdk.pad().ymin)
    pads = m << gf.grid(
        [pdk.pad] * 4,
        shape=(4, 1),
        spacing=(pad_spacing, pad_spacing),
        add_ports_prefix=False,
        add_ports_suffix=True,
    )
    pads.xmin = 360
    pads.ymin = 10

    # Places one experiment with gratings
    left_experiment_name = f"mzixtalk.gap.{gap:1.3f}.width.{width:1.3f}"
    left_exp = m << add_gc(
        mzi_xtalk(gap=gap, waveguide_width=width),
        with_loopback=False,
        component_name=left_experiment_name,
        fanout_length=100,
        optical_routing_type=1,
    )
    left_exp.xmin = floorplan.xmin + 20
    left_exp.ymax = floorplan.ymax - 20

    mzi_ports = [left_exp.ports["e2"], left_exp.ports["e1"]]
    pad_ports = [pads.ports["e1_0_0"], pads.ports["e1_1_0"]]
    dxs = [40, 30]
    dys = [0, 0]
    dx2s = [15, 15]
    for mzi_port, pad_port, dx, dy, dx2 in zip(mzi_ports, pad_ports, dxs, dys, dx2s):
        x0 = mzi_port.x
        y0 = mzi_port.y
        x2 = pad_port.x
        y2 = pad_port.y
        route = gf.routing.get_route_from_waypoints(
            [
                (x0, y0),
                (x0 + dx, y0),
                (x0 + dx, y2 + dy),
                (x2 - dx2, y2 + dy),
                (x2 - dx2, y2),
                (x2, y2),
            ],
            cross_section="xs_metal_routing",
            bend=gf.components.wire_corner,
        )
        m.add(route.references)

    # Add electrical labels
    for index, (padname, expname) in enumerate(
        zip(["G1", "S1"][::-1], [left_experiment_name, left_experiment_name])
    ):
        index += 2
        label = gf.component_layout.Label(
            text=f"elec_{expname}_{padname}",
            origin=(pads.xmin + 75 / 2, pads.ymin + (125) * index + 75 / 2),
            anchor="o",
            magnification=1.0,
            rotation=0.0,
            layer=layer_label[0],
            texttype=layer_label[1],
            x_reflection=False,
        )
        m.add(label)

    m.name = name
    return write_mask_gds_with_metadata(m)


test_mask_heating1 = gf.partial(
    test_mask_heating, gap=2, width=0.5, name="EBeam_heaters_simbilod_50"
)


test_mask_heating2 = gf.partial(
    test_mask_heating, gap=5, width=0.5, name="EBeam_heaters_simbilod_51"
)

test_mask_heating3 = gf.partial(
    test_mask_heating, gap=8, width=0.5, name="EBeam_heaters_simbilod_52"
)


test_mask_heating4 = gf.partial(
    test_mask_heating, gap=11, width=0.5, name="EBeam_heaters_simbilod_53"
)

test_mask_heating5 = gf.partial(
    test_mask_heating, gap=20, width=0.5, name="EBeam_heaters_simbilod_54"
)


test_mask_heating6 = gf.partial(
    test_mask_heating, gap=20, width=0.35, name="EBeam_heaters_simbilod_55"
)

test_mask_heating7 = gf.partial(
    test_mask_heating, gap=20, width=1.0, name="EBeam_heaters_simbilod_56"
)

if __name__ == "__main__":
    m = test_mask_heating6()
    # m = test_mask3()
    # m = test_mask4()
    # m = test_mask5()
    gf.show(m)
