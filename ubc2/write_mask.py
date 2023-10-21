"""Sample mask for the course."""
from functools import partial
from pathlib import Path

import gdsfactory as gf
import ubcpdk
from omegaconf import OmegaConf
from ubc1.config import PATH
from ubcpdk.tech import LAYER

size = (440, 470)
add_gc = ubcpdk.components.add_fiber_array
pack = partial(
    gf.pack, max_size=size, add_ports_prefix=False, add_ports_suffix=False, spacing=2
)


def write_mask_gds_with_metadata(m) -> Path:
    """Returns gdspath."""
    gdspath = PATH.build / f"{m.name}.gds"
    m.write_gds(gdspath=gdspath, with_metadata=True)
    metadata_path = gdspath.with_suffix(".yml")
    OmegaConf.load(metadata_path)
    gf.labels.write_labels.write_labels_gdstk(
        gdspath=gdspath, layer_label=LAYER.TEXT, debug=True
    )
    return gdspath
