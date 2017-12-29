# raspberry-scripts
Raspberry-Pi scripts for monitoring IrydPID (PL) coal stove computer.

Few main concepts:
1. Actual state monitoring. Stats are exported using NodeExporter (for Grafana/Influx charts). Data gathered by: 
  - ds18b20 termometers
  - input switches (alfa version of feeder state monitoring)
  - serial port to IrydPID computer (next version, more accurate results)
  - ...
2. Summary statistics generation (like estimating how long feeder can work with full coal supply)
3. Low temp and low-coal (calculated) state
