#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import numpy
import os

import ROOT

import TauPolSoftware.CalibrationCurve.getcalibrationcurve as getcalibrationcurve
import TauPolSoftware.CalibrationCurve.tools as tools


if __name__ == "__main__":
	
	parser = argparse.ArgumentParser(description="Combine the data of up-type and down-type quarks from ZFitter and using the NLOPDF and calculate their errors.")
	
	parser.add_argument("-z", "--zfitter-output", default="$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/data/zfitter.root",
	                    help="ZFitter output *.root file. [Default: %(default)s]")
	
	parser.add_argument("-e", "--energy-distributions-file", nargs="+",
	                    default="$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/data/energy_distributions.root",
	                    help="ROOT file  containing histogram(s) for u/d u/dbar -> Z events in bins of the true Z boson mass (u=u,c, d=d,s,b). [Default: %(default)s]")
	
	parser.add_argument("--sin2theta-min", type=float, default=0.150,
	                    help="Min. sin^2 theta_W value for scan. [Default: %(default)s]")
	parser.add_argument("--sin2theta-max", type=float, default=0.300,
	                    help="Max. sin^2 theta_W value for scan. [Default: %(default)s]")
	parser.add_argument("--sin2theta-delta", type=float, default=0.0025,
	                    help="Sin^2 theta_W step size for scan. [Default: %(default)s]")
	parser.add_argument("--sin2theta-mc", type=float, default=0.231295,
	                    help="Sin^2 theta_W value implemented in the MC sample. [Default: %(default)s]")
	
	parser.add_argument("-o", "--output-file", nargs="+",
	                    default="$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/data/calibration_curves.root",
	                    help="Output *.root file(s) and path(s) inside. Format: path/to/file.root:path/to/directory [Default: %(default)s]")
	
	args = parser.parse_args()
	
	# preparations
	args.energy_distributions_file = os.path.expandvars(args.energy_distributions_file)
	args.output_file = os.path.expandvars(args.output_file)
	
	energy_distributions_up = []
	energy_distributions_down = []
	elements = list(zip(*tools.walk_root_directory(args.energy_distributions_file))[-1])
	energy_distributions_up = [args.energy_distributions_file+":"+element for element in elements if element.endswith("up")]
	energy_distributions_down = [args.energy_distributions_file+":"+element for element in elements if element.endswith("down")]
	outputs = [args.output_file+":"+os.path.dirname(element) for element in elements if element.endswith("up")]
	
	sin2theta_edges = list(numpy.arange(args.sin2theta_min-0.5*args.sin2theta_delta, args.sin2theta_max+args.sin2theta_delta, args.sin2theta_delta))
	
	for energy_distribution_up, energy_distribution_down, output_path in zip(
		energy_distributions_up,
		energy_distributions_down,
		outputs
	):
		calibration_curve = getcalibrationcurve.CalibrationCurve(
				args.zfitter_output,
				[energy_distribution_up],
				[energy_distribution_down],
				sin2theta_edges,
				args.sin2theta_mc
		)
		calibration_curve.save_calibration_curves(output_path)
	
	# combination
	calibration_curve = getcalibrationcurve.CalibrationCurve(
			args.zfitter_output,
			energy_distributions_up,
			energy_distributions_down,
			sin2theta_edges,
			args.sin2theta_mc
	)
	calibration_curve.save_calibration_curves(args.output_file+":combined")

