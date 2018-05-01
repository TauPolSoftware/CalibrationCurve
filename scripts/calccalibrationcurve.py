#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import math
import numpy
import os

import ROOT

import TauPolSoftware.CalibrationCurve.tools as tools

# the calculations here use the uncertainties package for the error propagation
# use <return value>.nominal_value to retrive the central value
# http://uncertainties-python-package.readthedocs.io/en/latest/user_guide.html
import TauPolSoftware.CalibrationCurve.uncertainties.uncertainties as uncertainties


def get_weight_string(efficiency_histogram):
	efficiency_histogram.Scale(1.0 / efficiency_histogram.Integral())
	bin_edges = tools.get_bin_edges(efficiency_histogram)
	bin_contents = tools.get_bin_contents(efficiency_histogram)
	return " + ".join(["((energy>={low})*(energy<{high})*{content})".format(low=low, high=high, content=content) for low, high, content in zip(bin_edges[:-1], bin_edges[1:], bin_contents)])


if __name__ == "__main__":
	
	parser = argparse.ArgumentParser(description="Combine the data of up-type and down-type quarks from ZFitter and using the NLOPDF and calculate their errors.")
	
	parser.add_argument("--input-calibration", default="$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/data/calibration.root",
	                    help="Input *.root file containing calibration tree. [Default: %(default)s]")
	
	parser.add_argument("--input-efficiency", default="$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/data/genBosonLV_M__.root",
	                    help="Input *.root file containing efficiency histogram as a function of the energy. [Default: %(default)s]")
	parser.add_argument("--efficiency-histogram", default="ztt",
	                    help="Path to efficiency histogram inside *.root file. [Default: %(default)s]")
	
	parser.add_argument("--pol-binning", default=None,
	                    help="Binning for polarisation histogram. [Default: %(default)s]")
	parser.add_argument("--sin2theta-binning", default=None,
	                    help="Binning for sin^2 theta_W histogram. [Default: %(default)s]")
	
	parser.add_argument("-o", "--output", default="$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/data/calibrationcurve.root",
	                    help="Output *.root file. [Default: %(default)s]")
	
	args = parser.parse_args()
	args.input_calibration = os.path.expandvars(args.input_calibration)
	args.input_efficiency = os.path.expandvars(args.input_efficiency)
	args.output = os.path.expandvars(args.output)

	# Open ROOT file and extracting the example count histogram
	input_efficiency_file = ROOT.TFile(args.input_efficiency, "OPEN")
	efficiency_histogram = input_efficiency_file.Get(args.efficiency_histogram)
	efficiency_histogram.SetDirectory(0)
	input_efficiency_file.Close()
	
	# normalise efficiency histogram
	efficiency_histogram.Scale(1.0 / efficiency_histogram.Integral())
	
	input_calibration_file = ROOT.TFile(args.input_calibration, "OPEN")
	input_tree = input_calibration_file.Get("calibration")
	
	output_file = ROOT.TFile(args.output, "RECREATE")
	output_tree = input_tree.CloneTree(0)
	
	eff_branch = numpy.zeros(1, dtype=float)
	efferr_branch = numpy.zeros(1, dtype=float)
	output_tree.Branch("eff", eff_branch, "eff/D")
	output_tree.Branch("efferr", efferr_branch, "efferr/D")
	
	n_entries = input_tree.GetEntries()
	pol_values = {}
	eff_values = {}
	for entry in xrange(input_tree.GetEntries()):
		input_tree.GetEntry(entry)
		
		energy_bin = efficiency_histogram.FindBin(input_tree.energy)
		if (energy_bin < 1) or (energy_bin > efficiency_histogram.GetNbinsX()):
			eff_branch[0] = 0.0
			efferr_branch[0] = 0.0
		else:
			eff_branch[0] = efficiency_histogram.GetBinContent(energy_bin)
			efferr_branch[0] = efficiency_histogram.GetBinError(energy_bin)
		
		pol_values.setdefault(input_tree.sin2theta, []).append(uncertainties.ufloat(input_tree.pol, input_tree.polerr))
		eff_values.setdefault(input_tree.sin2theta, []).append(uncertainties.ufloat(eff_branch[0], efferr_branch[0]))
		
		output_tree.Fill()
	
	tools.write_object(output_file, output_tree, "calibration")
	
	final_calibration = {}
	for sin2theta_value, tmp_eff_values in eff_values.iteritems():
		pol_value = sum(numpy.array(pol_values[sin2theta_value]) * numpy.array(tmp_eff_values)) / sum(numpy.array(tmp_eff_values))
		final_calibration[sin2theta_value] = pol_value
	
	n_points = len(final_calibration)
	graph_values_sin2theta = numpy.array(sorted(final_calibration.keys()))
	graph_errors_sin2theta = numpy.array([0.0] * n_points)
	graph_values_pol = numpy.array([final_calibration[sin2theta_value].nominal_value for sin2theta_value in graph_values_sin2theta])
	graph_errors_pol = numpy.array([final_calibration[sin2theta_value].std_dev for sin2theta_value in graph_values_sin2theta])
	graph_values_pol_plus_sigma = graph_values_pol + graph_errors_pol
	graph_values_pol_minus_sigma = graph_values_pol - graph_errors_pol
	
	graph_sin2theta_vs_pol = ROOT.TGraphErrors(n_points, graph_values_pol, graph_values_sin2theta, graph_errors_pol, graph_errors_sin2theta)
	graph_sin2theta_vs_pol.GetXaxis().SetTitle("mixing angle")
	graph_sin2theta_vs_pol.GetYaxis().SetTitle("average polarisation")
	
	graph_pol_vs_sin2theta = ROOT.TGraphErrors(n_points, graph_values_sin2theta, graph_values_pol, graph_errors_sin2theta, graph_errors_pol)
	graph_sin2theta_vs_pol.GetXaxis().SetTitle("average polarisation")
	graph_sin2theta_vs_pol.GetYaxis().SetTitle("mixing angle")
	
	graph_sin2theta_vs_pol_plus_sigma = ROOT.TGraph(n_points, graph_values_pol_plus_sigma, graph_values_sin2theta)
	graph_sin2theta_vs_pol.GetXaxis().SetTitle("average polarisation +1#sigma")
	graph_sin2theta_vs_pol.GetYaxis().SetTitle("mixing angle")
	
	graph_sin2theta_vs_pol_minus_sigma = ROOT.TGraph(n_points, graph_values_pol_minus_sigma, graph_values_sin2theta)
	graph_sin2theta_vs_pol.GetXaxis().SetTitle("average polarisation -1#sigma")
	graph_sin2theta_vs_pol.GetYaxis().SetTitle("mixing angle")
	
	graph_pol_plus_sigma_vs_sin2theta = ROOT.TGraph(n_points, graph_values_sin2theta, graph_values_pol_plus_sigma)
	graph_sin2theta_vs_pol.GetXaxis().SetTitle("mixing angle")
	graph_sin2theta_vs_pol.GetYaxis().SetTitle("average polarisation +1#sigma")
	
	graph_pol_minus_sigma_vs_sin2theta = ROOT.TGraph(n_points, graph_values_sin2theta, graph_values_pol_minus_sigma)
	graph_sin2theta_vs_pol.GetXaxis().SetTitle("mixing angle")
	graph_sin2theta_vs_pol.GetYaxis().SetTitle("average polarisation -1#sigma")
	
	output_file.cd()
	tools.write_object(output_file, graph_sin2theta_vs_pol, "sin2theta_vs_pol")
	tools.write_object(output_file, graph_pol_vs_sin2theta, "pol_vs_sin2theta")
	tools.write_object(output_file, graph_sin2theta_vs_pol_plus_sigma, "sin2theta_vs_pol_plus_sigma")
	tools.write_object(output_file, graph_sin2theta_vs_pol_minus_sigma, "sin2theta_vs_pol_minus_sigma")
	tools.write_object(output_file, graph_pol_plus_sigma_vs_sin2theta, "pol_plus_sigma_vs_sin2theta")
	tools.write_object(output_file, graph_pol_minus_sigma_vs_sin2theta, "pol_minus_sigma_vs_sin2theta")
	
	output_file.Close()
	print "Saved outputs in\n\t{output_file}".format(output_file=args.output)

