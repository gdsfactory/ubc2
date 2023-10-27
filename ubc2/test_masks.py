"""Write all mask for the course."""
import shutil

from ubcpdk.config import PATH

import ubc2.ubc_helge as m12
import ubc2.ubc_joaquin_matres1 as m11
import ubc2.ubc_simon as m13
import ubc2.ubc_simon_bends as bends
import ubc2.ubc_simon_dcs as dcs
import ubc2.ubc_simon_loss as loss
import ubc2.ubc_simon_rings as rings


def test_masks_2023_v1():
    """Write all masks for 2023_v1."""
    dirpath = PATH.mask
    dirpath_gds = dirpath / "gds"

    if dirpath.exists():
        shutil.rmtree(dirpath)
    dirpath_gds.mkdir(exist_ok=True, parents=True)

    for mask in [
        m11.test_mask1,
        m11.test_mask2,
        m11.test_mask3,
        m11.test_mask4,
        m11.test_mask5,
        m11.test_mask6,
        m11.test_mask7,
        m12.test_mask1,
        m12.test_mask2,
        m13.test_mask1,
        m13.test_mask3,
        m13.test_mask4,
        m13.test_mask5,
        bends.test_mask_bends_circular,
        bends.test_mask_bends_euler,
        loss.test_mask_continuum,
        rings.test_mask_rings_1,
        rings.test_mask_rings_2,
        rings.test_mask_rings_3,
        dcs.test_mask_dcs_1,
        dcs.test_mask_dcs_2,
        dcs.test_mask_dcs_3,
        dcs.test_mask_dcs_4,
        dcs.test_mask_dcs_5,
        dcs.test_mask_dcs_6,
    ]:
        mask()

    for gdspath in dirpath.glob("*.gds"):
        shutil.copyfile(gdspath, dirpath_gds / f"{gdspath.name}")


if __name__ == "__main__":
    test_masks_2023_v1()
