# Spectral libraries

The in-house UT Austin spectral libraries (e.g. `UT_Austin_in_house_V3_mixRT_*.json`) are
**not tracked in git** (see `.gitignore`) — they are lab-internal reference data.

On POD they live at:
`/stor/work/Sedio/user_directories/dlf2493/2026_Chem_Ecol_Projects/pipeline/libraries/`

Pass the path explicitly when building a batch, e.g.
`update_mzmine_batch.py --library /path/to/UT_Austin_in_house_V3_mixRT_<date>.json`
