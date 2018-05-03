#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import hashlib
import numpy
import os

import ROOT

import TauPolSoftware.CalibrationCurve.tools as tools

# the calculations here use the uncertainties package for the error propagation
# use <return value>.nominal_value to retrive the central value
# http://uncertainties-python-package.readthedocs.io/en/latest/user_guide.html
import TauPolSoftware.CalibrationCurve.uncertainties.uncertainties as uncertainties


def get_histogram(path):
	splitted_path = path.split(":")
	input_file = ROOT.TFile(splitted_path[0], "OPEN")
	histogram = input_file.Get(splitted_path[-1])
	histogram.SetDirectory(0)
	input_file.Close()
	return histogram

def get_zfitter_polarisation_histogram(zfitter_output_path, sin2theta_min, sin2theta_max, energy_binning_histogram, quark_type):
	zfitter_tree = ROOT.TChain("zfitter_{quark_type}".format(quark_type=quark_type))
	zfitter_tree.Add(zfitter_output_path)
	
	histogram_name = "zfitter_polarisation_{quark_type}".format(quark_type=quark_type)+hashlib.md5("".join([str(item) for item in [zfitter_output_path, sin2theta_min, sin2theta_max, energy_binning_histogram, quark_type]])).hexdigest()
	binning = tools.get_binning(energy_binning_histogram)
	histogram = ROOT.TProfile(histogram_name, histogram_name, len(binning)-1, binning)
	
	zfitter_tree.Project(histogram_name, "pol:energy", "(sin2theta>={sin2theta_min})*(sin2theta<{sin2theta_max})".format(
			sin2theta_min=sin2theta_min,
			sin2theta_max=sin2theta_max
	), "prof goff")
	
	histogram = ROOT.gDirectory.Get(histogram_name).ProjectionX() # projection to convert into TH1
	return histogram

def get_polarisation(polarisation_histogram_up, polarisation_histogram_down, energy_histogram_up, energy_histogram_down):
	polarisation_histogram_up.Multiply(energy_histogram_up)
	polarisation_histogram_down.Multiply(energy_histogram_down)
	
	integral_polarisation_energy_up = polarisation_histogram_up.Integral()
	integral_polarisation_energy_down = polarisation_histogram_down.Integral()
	
	integral_energy_up = energy_histogram_up.Integral()
	integral_energy_down = energy_histogram_down.Integral()
	
	numerator = (integral_polarisation_energy_up + integral_polarisation_energy_down)
	denominator = (integral_energy_up + integral_energy_down)
	polarisation = 0.0
	if denominator != 0.0:
		polarisation = numerator / denominator
	return polarisation

def calculate_polarisation(zfitter_output_path, sin2theta_min, sin2theta_max, energy_histogram_up, energy_histogram_down):
	polarisation_histogram_up = get_zfitter_polarisation_histogram(zfitter_output_path, sin2theta_min, sin2theta_max, energy_histogram_up, "up")
	polarisation_histogram_down = get_zfitter_polarisation_histogram(zfitter_output_path, sin2theta_min, sin2theta_max, energy_histogram_down, "down")
	return get_polarisation(polarisation_histogram_up, polarisation_histogram_down, energy_histogram_up, energy_histogram_down)

def get_polarisation_values(zfitter_output_path, sin2theta_edges, energy_histogram_up, energy_histogram_down):
	polarisation_values = []
	for sin2theta_min, sin2theta_max in zip(sin2theta_edges[:-1], sin2theta_edges[1:]):
		polarisation_values.append(calculate_polarisation(zfitter_output_path, sin2theta_min, sin2theta_max, energy_histogram_up, energy_histogram_down))
	return polarisation_values


if __name__ == "__main__":
	
	parser = argparse.ArgumentParser(description="Combine the data of up-type and down-type quarks from ZFitter and using the NLOPDF and calculate their errors.")
	
	parser.add_argument("-z", "--zfitter-output", default="$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/data/zfitter.root",
	                    help="ZFitter output *.root file. [Default: %(default)s]")
	
	parser.add_argument("-u", "--energy-distribution-up",
	                    help="Histogram containing u ubar -> Z events in bins of the true Z boson mass (u=u,c). Format: path/to/file.root:path/to/histogram.")
	parser.add_argument("-d", "--energy-distribution-down",
	                    help="Histogram containing d dbar -> Z events in bins of the true Z boson mass (d=d,s,b). Format: path/to/file.root:path/to/histogram.")
	
	parser.add_argument("--sin2theta-min", type=float, default=0.150,
	                    help="Min. sin^2 theta_W value for scan. [Default: %(default)s]")
	parser.add_argument("--sin2theta-max", type=float, default=0.300,
	                    help="Max. sin^2 theta_W value for scan. [Default: %(default)s]")
	parser.add_argument("--sin2theta-delta", type=float, default=0.0025,
	                    help="Sin^2 theta_W step size for scan. [Default: %(default)s]")
	
	parser.add_argument("-o", "--output", default="$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/data/calibrationcurve.root",
	                    help="Output *.root file. [Default: %(default)s]")
	
	args = parser.parse_args()
	args.zfitter_output = os.path.expandvars(args.zfitter_output)
	args.energy_distribution_up = os.path.expandvars(args.energy_distribution_up)
	args.energy_distribution_down = os.path.expandvars(args.energy_distribution_down)
	args.output = os.path.expandvars(args.output)
	
	sin2theta_values = list(numpy.arange(args.sin2theta_min, args.sin2theta_max+args.sin2theta_delta, args.sin2theta_delta))
	sin2theta_edges = list(numpy.arange(args.sin2theta_min-0.5*args.sin2theta_delta, args.sin2theta_max+args.sin2theta_delta, args.sin2theta_delta))

	energy_distribution_up = get_histogram(args.energy_distribution_up)
	energy_distribution_down = get_histogram(args.energy_distribution_down)
	
	polarisation_values = get_polarisation_values(args.zfitter_output, sin2theta_edges, energy_distribution_up, energy_distribution_down)
	
	final_calibration = {uncertainties.ufloat(sin2theta_value, 0.0) : uncertainties.ufloat(polarisation_value, 0.0) for sin2theta_value, polarisation_value in zip(sin2theta_values, polarisation_values)}
	
	output_file = ROOT.TFile(args.output, "RECREATE")
	
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

