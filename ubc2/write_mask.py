"""Sample mask for the course."""
from functools import partial
from pathlib import Path

import gdsfactory as gf
import ubcpdk
from omegaconf import OmegaConf
from ubcpdk.tech import LAYER

from ubc2.config import PATH

size_actives = (440, 470)
size  = (605, 410)
add_gc = ubcpdk.components.add_fiber_array
pack = partial(
    gf.pack, max_size=size, add_ports_prefix=False, add_ports_suffix=False, spacing=2
)
pack_actives = partial(pack, max_size=size_actives)


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
