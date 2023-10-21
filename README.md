# ubc2 0.0.1

[edx course](https://www.edx.org/course/silicon-photonics-design-fabrication-and-data-ana) submission for 2023 October

## Installation

`make install`


## Upload design

We have a GitHub action that builds the mask on every git push.

- You can upload the GDS files into [nextcloud](https://qdot-nexus.phas.ubc.ca:25683/index.php/s/Xew2p7PrE2kgHNW)
- After uploading your layout, once every three minutes, our automated system checks your layout and produces a text log file including some errors: [EBeam.txt](https://qdot-nexus.phas.ubc.ca:25683/s/gkN3zq4KSFgcTBD/download?path=%2F&files=EBeam.txt)
- The system also merges all participant layouts into a single file.  You can download the merged layout from: [EBeam.gds](https://qdot-nexus.phas.ubc.ca:25683/s/gkN3zq4KSFgcTBD/download?path=%2F&files=EBeam.gds) or [EBeam.oas (~10X smaller)](https://qdot-nexus.phas.ubc.ca:25683/s/gkN3zq4KSFgcTBD/download?path=%2F&files=EBeam.oas)


## Optional: Heaters

- [heater slides from course](https://docs.google.com/presentation/d/1_ppHYec6LydML4RMRJdNI4DXHb0hgW7znToQCGgSF6M/edit#slide=id.g1d6f54b2122_1_164)
- [ubc slides](https://docs.google.com/presentation/d/17FWUaRZ0zKV5zrPgY4fo98M8ywtmE3blaxkwUvk_7yM/edit#slide=id.g1f32360cef6_0_11)

Filename requirements:

```
        EBeam_heaters_<USERNAME>.oas, or .gds
```

- Submit your design to the following [server](https://qdot-nexus.phas.ubc.ca:25683/s/mwQTSzwq99dj6Ym)
- See all the individual [file submissions](https://qdot-nexus.phas.ubc.ca:25683/s/s8eQLKBkAcTaH2e)
- Download the [merged layout](https://qdot-nexus.phas.ubc.ca:25683/s/P6jxBMWyzWywrqw)
