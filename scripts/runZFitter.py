#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import numpy
import os

import TauPolSoftware.CalibrationCurve.tools as tools
import TauPolSoftware.CalibrationCurve.runzfitter as runzfitter


if __name__ == "__main__":
	
	parser = argparse.ArgumentParser(description="Run (modified) ZFitter. Obtaining P(sqrt s) and sigma(sqrt s) from ZFitter for different sin^2 theta_W and setting range and steps of energy for which the values should be calculated. See also http://cds.cern.ch/record/265101/files/9412201.pdf")
	
	parser.add_argument("--sin2theta-min", type=float, default=0.10,
	                    help="Min. sin^2 theta_W value for scan. [Default: %(default)s]")
	parser.add_argument("--sin2theta-max", type=float, default=0.35,
	                    help="Max. sin^2 theta_W value for scan. [Default: %(default)s]")
	parser.add_argument("--sin2theta-delta", type=float, default=0.0025,
	                    help="Sin^2 theta_W step size for scan. [Default: %(default)s]")
	
	parser.add_argument("--energy-min", type=float, default=35.0,
	                    help="Min. sqrt(s) value for scan. [Default: %(default)s]")
	parser.add_argument("--energy-max", type=float, default=350.0,
	                    help="Max. sqrt(s) value for scan. [Default: %(default)s]")
	parser.add_argument("--energy-delta", type=float, default=0.25,
	                    help="Sqrt(s) step size for scan. [Default: %(default)s]")
	
	parser.add_argument("-o", "--output", default="$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/data/zfitter.root",
	                    help="Output *.root file. [Default: %(default)s]")

	parser.add_argument("-n", "--n-processes", type=int, default=1,
	                    help="Number of (parallel) processes. [Default: %(default)s]")
	
	args = parser.parse_args()
	args.output = os.path.expandvars(args.output)
	
	sin2theta_values = list(numpy.arange(args.sin2theta_min, args.sin2theta_max+args.sin2theta_delta, args.sin2theta_delta))
	
	energy_steps = (args.energy_max-args.energy_min)/args.energy_delta+1
	energy_values = list(numpy.arange(args.energy_min, args.energy_max+args.energy_delta, args.energy_delta))
	
	quark_types = ["D", "U"]
	
	get_zfitter_executable_args = [[
			quark_type,
			sin2theta_value,
			"{value:05}".format(value=int(sin2theta_value*10000)),
			str(len(energy_values)),
			str(args.energy_min),
			str(args.energy_delta),
	] for quark_type in quark_types for sin2theta_value in sin2theta_values]
	
	run_zfitter_args = tools.parallelize(runzfitter.get_zfitter_executable, get_zfitter_executable_args, n_processes=1, description="Compile ZFitter executables")
	tmp_zfitter_outputs = tools.parallelize(runzfitter.run_zfitter, run_zfitter_args, n_processes=args.n_processes, description="Run ZFitter")
	
	zfitter_outputs = {}
	for tmp_zfitter_output in tmp_zfitter_outputs:
		for quark_type, zfitter_output in tmp_zfitter_output.iteritems():
			zfitter_outputs.setdefault(quark_type, []).append(zfitter_output)
	runzfitter.collect_zfitter_outputs(zfitter_outputs, args)

