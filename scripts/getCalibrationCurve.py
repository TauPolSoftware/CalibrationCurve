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
	parser.add_argument("--sin2theta-mc", type=float, default=0.229043375, # corresponding to <P_tau> = -0.167653
	                    help="Sin^2 theta_W value implemented in the MC sample. [Default: %(default)s]")
	
	parser.add_argument("-o", "--output-file",
	                    default="$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/data/calibration_curves.root",
	                    help="Output *.root file. [Default: %(default)s]")
	
	args = parser.parse_args()
	
	# preparations
	args.energy_distributions_file = os.path.expandvars(args.energy_distributions_file)
	args.output_file = os.path.expandvars(args.output_file)
	
	energy_distributions_up = []
	energy_distributions_down = []
	elements = list(zip(*tools.walk_root_directory(args.energy_distributions_file))[-1])
	
	categories = sorted(list(set([element.split("/")[0] for element in elements])))
	# quark_types = sorted(list(set([element.split("/")[1] for element in elements])))
	systematics = sorted(list(set([element.split("/")[2].replace("_up", "").replace("_down", "") for element in elements if not "nominal" in element])))
	print "Found categories:", categories
	# print "Found quark types:", quark_types
	print "Found systematics:", systematics
	
	sin2theta_edges = list(numpy.arange(args.sin2theta_min-0.5*args.sin2theta_delta, args.sin2theta_max+args.sin2theta_delta, args.sin2theta_delta))
	
	calibration_curves = {}
	file_option = "RECREATE"
	for index_systematic, systematic in enumerate(["nominal"]+systematics):
		for systematic_shift in ([""] if index_systematic == 0 else ["_up", "_down"]):
			for index_category, tmp_categories in enumerate([categories]+[[category] for category in categories]):
				energy_distributions_up = [args.energy_distributions_file+":"+os.path.join(category, "up", systematic+systematic_shift) for category in tmp_categories]
				energy_distributions_down = [args.energy_distributions_file+":"+os.path.join(category, "down", systematic+systematic_shift) for category in tmp_categories]
				output_directory = args.output_file+":"+os.path.join("combined" if index_category == 0 else category, systematic+systematic_shift)
				
				calibration_curve = getcalibrationcurve.CalibrationCurve(
						args.zfitter_output,
						energy_distributions_up,
						energy_distributions_down,
						sin2theta_edges,
						args.sin2theta_mc
				)
				calibration_curve.save_calibration_curves(output_directory, file_option)
				file_option = "UPDATE"
				
				if index_systematic == 0:
					calibration_curves.setdefault("combined" if index_category == 0 else category, {})[systematic] = calibration_curve
				else:
					calibration_curves.setdefault("combined" if index_category == 0 else category, {}).setdefault(systematic, {})[systematic_shift.replace("_", "")] = calibration_curve
	
	# combine uncertainties
	for category, data in calibration_curves.iteritems():
		calibration_curve = getcalibrationcurve.combine_uncertainties(
				nominal=data["nominal"],
				shifts_up=[shift["up"] for syst, shift in data.iteritems() if syst != "nominal"],
				shifts_down=[shift["down"] for syst, shift in data.iteritems() if syst != "nominal"]
		)
		output_directory = args.output_file+":"+os.path.join(category, "combined_uncs")
		calibration_curve.save_calibration_curves(output_directory, file_option)

