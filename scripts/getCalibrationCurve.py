#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import numpy
import os

import TauPolSoftware.CalibrationCurve.getcalibrationcurve as getcalibrationcurve


if __name__ == "__main__":
	
	channels = ["tt", "mt", "et"]
	categories = [
			"a1", "a1_1", "a1_2",
			"rho", "rho_1", "rho_2",
			"oneprong", "oneprong_1", "oneprong_2",
			"combined_a1_a1", "combined_a1_rho", "combined_a1_oneprong",
			"combined_rho_rho", "combined_rho_oneprong",
			"combined_oneprong_oneprong"
	]
	default_directories = [channel+"_"+category for channel in channels for category in categories]
	default_energy_distributions_file = "$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/data/energy_distributions.root"
	default_energy_distributions_up = [default_energy_distributions_file+":"+os.path.join(directory, "up") for directory in default_directories]
	default_energy_distributions_down = [default_energy_distributions_file+":"+os.path.join(directory, "down") for directory in default_directories]
	default_outputs = [default_energy_distributions_file+":"+directory for directory in default_directories]
	
	parser = argparse.ArgumentParser(description="Combine the data of up-type and down-type quarks from ZFitter and using the NLOPDF and calculate their errors.")
	
	parser.add_argument("-z", "--zfitter-output", default="$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/data/zfitter.root",
	                    help="ZFitter output *.root file. [Default: %(default)s]")
	
	parser.add_argument("-u", "--energy-distributions-up", nargs="+",
	                    default=default_energy_distributions_up,
	                    help="Histogram(s) containing u ubar -> Z events in bins of the true Z boson mass (u=u,c). Format: path/to/file.root:path/to/histogram. [Default: %(default)s]")
	parser.add_argument("-d", "--energy-distributions-down", nargs="+",
	                    default=default_energy_distributions_down,
	                    help="Histogram(s) containing d dbar -> Z events in bins of the true Z boson mass (d=d,s,b). Format: path/to/file.root:path/to/histogram. [Default: %(default)s]")
	
	parser.add_argument("--sin2theta-min", type=float, default=0.150,
	                    help="Min. sin^2 theta_W value for scan. [Default: %(default)s]")
	parser.add_argument("--sin2theta-max", type=float, default=0.300,
	                    help="Max. sin^2 theta_W value for scan. [Default: %(default)s]")
	parser.add_argument("--sin2theta-delta", type=float, default=0.0025,
	                    help="Sin^2 theta_W step size for scan. [Default: %(default)s]")
	parser.add_argument("--sin2theta-mc", type=float, default=0.231295,
	                    help="Sin^2 theta_W value implemented in the MC sample. [Default: %(default)s]")
	
	parser.add_argument("-o", "--outputs", nargs="+",
	                    default=default_outputs,
	                    help="Output *.root file(s) and path(s) inside. Format: path/to/file.root:path/to/directory [Default: %(default)s]")
	
	args = parser.parse_args()
	
	sin2theta_edges = list(numpy.arange(args.sin2theta_min-0.5*args.sin2theta_delta, args.sin2theta_max+args.sin2theta_delta, args.sin2theta_delta))
	
	for energy_distribution_up, energy_distribution_down, output_path in zip(
		args.energy_distributions_up,
		args.energy_distributions_down,
		args.outputs
	):
		calibration_curve = getcalibrationcurve.CalibrationCurve(
				args.zfitter_output,
				energy_distribution_up,
				energy_distribution_down,
				sin2theta_edges,
				args.sin2theta_mc
		)
		calibration_curve.save_calibration_curves(output_path)

