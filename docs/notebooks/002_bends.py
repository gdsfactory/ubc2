# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.15.2
#   kernelspec:
#     display_name: Python 3
#     name: python3
# ---

# # Bent waveguide losses

# + tags=["hide-input"]
from collections import OrderedDict

import matplotlib.pyplot as plt
import numpy as np
from femwell.maxwell.waveguide import compute_modes
from femwell.mesh import mesh_from_OrderedDict
from shapely import box
from shapely.ops import clip_by_rect
from skfem import Basis, ElementDG, ElementTriP1
from skfem.io.meshio import from_meshio
from tqdm import tqdm

# -

# We describe the geometry using shapely.
# In this case it's simple: we use a shapely.box for the waveguide.
# For the surrounding we buffer the core and clip it to the part below the waveguide for the box.
# The remaining buffer is used as the clad.
# For the core we set the resolution to 30nm and let it fall of over 500nm

# +
wavelength = 1.55

wg_width = 0.5
wg_thickness = 0.22
pml_distance = wg_width / 2 + 2  # distance from center
pml_thickness = 2
core = box(-wg_width / 2, 0, wg_width / 2, wg_thickness)
env = box(-1 - wg_width / 2, -1, pml_distance + pml_thickness, wg_thickness + 1)

polygons = OrderedDict(
    core=core,
    box=clip_by_rect(env, -np.inf, -np.inf, np.inf, 0),
    clad=clip_by_rect(env, -np.inf, 0, np.inf, np.inf),
)

resolutions = dict(
    core={"resolution": 0.03, "distance": 1}, slab={"resolution": 0.1, "distance": 0.5}
)

mesh = from_meshio(
    mesh_from_OrderedDict(
        polygons, resolutions, default_resolution_max=0.2, filename="mesh.msh"
    )
)
mesh.draw().show()
# -

# On this mesh, we define the epsilon. We do this by setting domainwise the epsilon to the squared refractive index.
# We additionally add a PML layer bt adding a imaginary part to the epsilon

basis0 = Basis(mesh, ElementDG(ElementTriP1()))
epsilon = basis0.zeros(dtype=complex)
for subdomain, n in {"core": 3.48, "box": 1.444, "clad": 1.444}.items():
    epsilon[basis0.get_dofs(elements=subdomain)] = n**2
epsilon += basis0.project(
    lambda x: -10j * np.maximum(0, x[0] - pml_distance) ** 2,
    dtype=complex,
)
basis0.plot(epsilon.real, shading="gouraud", colorbar=True).show()
basis0.plot(epsilon.imag, shading="gouraud", colorbar=True).show()

# We calculate now the modes for the geometry we just set up.
# We do it first for the case, where the bend-radius is infinite, i.e. a straight waveguide.
# This is done to have a reference effectie refractive index for starting
# and for mode overlap calculations between straight and bent waveguides.

modes_straight = compute_modes(
    basis0, epsilon, wavelength=wavelength, num_modes=1, order=2, radius=np.inf
)

# Now we calculate the modes of bent waveguides with different radii.
# Subsequently, we calculate the overlap integrals between the modes to determine the coupling efficiency
# And determine from the imaginary part the bend loss.

# + tags=["remove-stderr"]
radiuss = np.linspace(20, 1, 11)
radiuss_lams = []
overlaps = []
lam_guess = modes_straight[0].n_eff
for radius in tqdm(radiuss):
    modes = compute_modes(
        basis0,
        epsilon,
        wavelength=wavelength,
        num_modes=1,
        order=2,
        radius=radius,
        n_guess=lam_guess,
        solver="scipy",
    )
    lam_guess = modes[0].n_eff
    radiuss_lams.append(modes[0].n_eff)

    overlaps.append(modes_straight[0].calculate_overlap(modes[0]))
# -

# And now we plot it!

# + tags=["hide-input"]
plt.xlabel("Radius / μm")
plt.ylabel("Mode overlap loss with straight waveguide mode / dB")
plt.yscale("log")
plt.plot(radiuss, -10 * np.log10(np.abs(overlaps) ** 2))
plt.show()
plt.xlabel("Radius / μm")
plt.ylabel("90-degree bend transmission / dB")
plt.yscale("log")
plt.plot(
    radiuss,
    -10
    * np.log10(
        np.exp(
            -2 * np.pi / wavelength * radius * np.abs(np.imag(radiuss_lams)) * np.pi / 2
        )
    ),
)
plt.show()
# -

# We now plot the mode calculated for the smallest bend radius to check that it's still within the waveguide.
# As modes can have complex fields as soon as the epsilon gets complex, so we get a complex field for each mode.
# Here we show only the real part of the mode.

# + tags=["hide-input"]
for mode in modes:
    print(f"Effective refractive index: {mode.n_eff:.14f}")
    mode.plot(mode.E.real, colorbar=True, direction="x")
    plt.show()

# -

# The loss is dominated by mode mismatch. Loss for variable number of bends, with >2dB target for measurable signal:

for n_bends in [100, 120, 140, 160]:
    plt.xlabel("Radius / μm")
    plt.ylabel(f"Loss for {n_bends} bends")
    plt.yscale("log")
    plt.plot(radiuss, n_bends * (-10 * np.log10(np.abs(overlaps) ** 2)))
    plt.axhline(y=2, color="r", linestyle="--")
    plt.axvline(x=2, color="g", linestyle="--")
    plt.axvline(x=4, color="b", linestyle="--")
    plt.axvline(x=6, color="y", linestyle="--")
    plt.show()
