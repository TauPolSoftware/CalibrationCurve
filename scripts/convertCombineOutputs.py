#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import numpy
import os

import ROOT

import TauPolSoftware.CalibrationCurve.tools as tools


if __name__ == "__main__":
	
	parser = argparse.ArgumentParser(description="Convert combine outputs from polarisation fits.")
	
	parser.add_argument("combine_output",
	                    help="Combine *.root output files containing limit tree with pol branch.")
	parser.add_argument("-c", "--calibration-curves", default="$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/data/calibrationcurve.root",
	                    help="*.root files containing calibration curves. [Default: %(default)s]")
	
	args = parser.parse_args()
	args.combine_output = os.path.expandvars(args.combine_output)
	args.calibration_curves = os.path.expandvars(args.calibration_curves)
	
	calibration_curves_file = ROOT.TFile(args.calibration_curves, "OPEN")
	
	graph_sin2theta_vs_pol = calibration_curves_file.Get("sin2theta_vs_pol")
	#graph_pol_vs_sin2theta = calibration_curves_file.Get("pol_vs_sin2theta")
	#graph_sin2theta_vs_pol_plus_sigma = calibration_curves_file.Get("sin2theta_vs_pol_plus_sigma")
	#graph_sin2theta_vs_pol_minus_sigma = calibration_curves_file.Get("sin2theta_vs_pol_minus_sigma")
	#graph_pol_plus_sigma_vs_sin2theta = calibration_curves_file.Get("pol_plus_sigma_vs_sin2theta")
	#graph_pol_minus_sigma_vs_sin2theta = calibration_curves_file.Get("pol_minus_sigma_vs_sin2theta")
	
	calibration_curves_file.Close()
	
	combine_output_file = ROOT.TFile(args.combine_output, "UPDATE")
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
	combine_output_file.Close()
	print "Saved conversion in\n\t{output_file}".format(output_file=args.combine_output)

