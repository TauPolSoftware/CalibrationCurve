#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import numpy
import os

import ROOT

import TauPolSoftware.CalibrationCurve.tools as tools
import TauPolSoftware.CalibrationCurve.tfilecontextmanager as tfilecontextmanager


if __name__ == "__main__":
	
	parser = argparse.ArgumentParser(description="Convert combine outputs from polarisation fits.")
	
	parser.add_argument("combine_output",
	                    help="Combine ROOT output file containing limit tree with pol branch.")
	parser.add_argument("-c", "--calibration-curve", default="$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/data/calibration_curves.root:combined",
	                    help="ROOT file containing and directory inside calibration curve(s). Format: file.root:directory. [Default: %(default)s]")
	
	args = parser.parse_args()
	args.combine_output = os.path.expandvars(args.combine_output)
	args.calibration_curve = os.path.expandvars(args.calibration_curve)
	
	graph_sin2theta_vs_pol = None
	graph_pol_vs_sin2theta = None
	graph_sin2theta_vs_pol_plus_sigma = None
	graph_sin2theta_vs_pol_minus_sigma = None
	graph_pol_plus_sigma_vs_sin2theta = None
	graph_pol_minus_sigma_vs_sin2theta = None
	with tfilecontextmanager.TFileContextManager(args.calibration_curve.split(":")[0], "OPEN") as calibration_curves_file:
		graph_sin2theta_vs_pol = calibration_curves_file.Get(os.path.join(args.calibration_curve.split(":")[-1] if ":" in args.calibration_curve else "", "sin2theta_vs_pol"))
		#graph_pol_vs_sin2theta = calibration_curves_file.Get(os.path.join(args.calibration_curve.split(":")[-1] if ":" in args.calibration_curve else "", "pol_vs_sin2theta"))
		#graph_sin2theta_vs_pol_plus_sigma = calibration_curves_file.Get(os.path.join(args.calibration_curve.split(":")[-1] if ":" in args.calibration_curve else "", "sin2theta_vs_pol_plus_sigma"))
		#graph_sin2theta_vs_pol_minus_sigma = calibration_curves_file.Get(os.path.join(args.calibration_curve.split(":")[-1] if ":" in args.calibration_curve else "", "sin2theta_vs_pol_minus_sigma"))
		#graph_pol_plus_sigma_vs_sin2theta = calibration_curves_file.Get(os.path.join(args.calibration_curve.split(":")[-1] if ":" in args.calibration_curve else "", "pol_plus_sigma_vs_sin2theta"))
		#graph_pol_minus_sigma_vs_sin2theta = calibration_curves_file.Get(os.path.join(args.calibration_curve.split(":")[-1] if ":" in args.calibration_curve else "", "pol_minus_sigma_vs_sin2theta"))
	
	with tfilecontextmanager.TFileContextManager(args.combine_output, "UPDATE") as combine_output_file:
		limit_tree = combine_output_file.Get("limit")
		
		pol = 0.0
		pol_minus_sigma = 0.0
		pol_plus_sigma = 0.0
		for entry in xrange(limit_tree.GetEntries()):
			limit_tree.GetEntry(entry)
			if entry == 0:
				pol = limit_tree.pol
			elif entry == 1:
				pol_minus_sigma = limit_tree.pol
			elif entry == 2:
				pol_plus_sigma = limit_tree.pol
			else:
				print "Warning: check interpretation of tree entries!"
		
		# no error propagation from calibration curve so far...
		sin2theta = graph_sin2theta_vs_pol.Eval(pol)
		sin2theta_minus_sigma = graph_sin2theta_vs_pol.Eval(pol_minus_sigma)
		sin2theta_plus_sigma = graph_sin2theta_vs_pol.Eval(pol_plus_sigma)
		
		sin2theta_tree = ROOT.TTree()
		sin2theta_tree.SetName("sin2theta")
		sin2theta_branch = numpy.zeros(1, dtype=float)
		sin2theta_tree.Branch("sin2theta", sin2theta_branch, "sin2theta/D")
		
		sin2theta_branch[0] = sin2theta
		sin2theta_tree.Fill()
		sin2theta_branch[0] = sin2theta_minus_sigma
		sin2theta_tree.Fill()
		sin2theta_branch[0] = sin2theta_plus_sigma
		sin2theta_tree.Fill()
		
		sin2theta_tree.AddFriend(limit_tree, limit_tree.GetName())
		limit_tree.AddFriend(sin2theta_tree, sin2theta_tree.GetName())
		
		tools.write_object(combine_output_file, sin2theta_tree, sin2theta_tree.GetName())
		combine_output_file.Write()
	
	print "Saved conversion in\n\t{output_file}".format(output_file=args.combine_output)

