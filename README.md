# py-fpga-scope

[WIP] Python tools to snoop, debug, and show FPGA signals using JTAG commands.

Initially, it will be developed for intel-FPGAs, using IPs to access
data through JTAG.
# Milestones

[ ] Access quartus tcl through Python.
[ ] Detect the hardwares and devices available.
[ ] Detect the in-system source-probes available.
[ ] Detect the in-system memories available.
[ ] Access and parse the source-probe data.
[ ] Access and parse the memory data.
[ ] Create FPGA module to same a frame from the signal.
[ ] Create a python controller drive the FPGA module.
[ ] Collect the memory data periocally.
[ ] Create UI to show in real-time the channels.
[ ] Enable operation with the data and show real-time.
[ ] Come up with tests.
[ ] Provide this code in PyPi.
