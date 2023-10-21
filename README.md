# ubc2 0.0.1

edx course submission for 2023 October

## Installation

`make install`


## Upload design

We have a GitHub action that builds the mask on every git push.

- You can upload the GDS files into [nextcloud](https://qdot-nexus.phas.ubc.ca:25683/index.php/s/Xew2p7PrE2kgHNW)
- After uploading your layout, once every three minutes, our automated system checks your layout and produces a text log file including some errors: [EBeam.txt](https://qdot-nexus.phas.ubc.ca:25683/s/gkN3zq4KSFgcTBD/download?path=%2F&files=EBeam.txt)
- The system also merges all participant layouts into a single file.  You can download the merged layout from: [EBeam.gds](https://qdot-nexus.phas.ubc.ca:25683/s/gkN3zq4KSFgcTBD/download?path=%2F&files=EBeam.gds) or [EBeam.oas (~10X smaller)](https://qdot-nexus.phas.ubc.ca:25683/s/gkN3zq4KSFgcTBD/download?path=%2F&files=EBeam.oas)
