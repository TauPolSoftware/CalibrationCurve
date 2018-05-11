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
	input_file_path, histogram_path = path.split(":")
	input_file = ROOT.TFile(input_file_path, "OPEN")
	histogram = input_file.Get(histogram_path)
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

def get_calibration_curve(zfitter_output_path, energy_distribution_up_path, energy_distribution_down_path, sin2theta_values, sin2theta_edges, output_path):

	zfitter_output_path = os.path.expandvars(zfitter_output_path)
	energy_distribution_up_path = os.path.expandvars(energy_distribution_up_path)
	energy_distribution_down_path = os.path.expandvars(energy_distribution_down_path)
	output_path = os.path.expandvars(output_path)
	
	energy_distribution_up = get_histogram(energy_distribution_up_path)
	energy_distribution_down = get_histogram(energy_distribution_down_path)
	
	polarisation_values = get_polarisation_values(zfitter_output_path, sin2theta_edges, energy_distribution_up, energy_distribution_down)
	
	final_calibration = {uncertainties.ufloat(sin2theta_value, 0.0) : uncertainties.ufloat(polarisation_value, 0.0) for sin2theta_value, polarisation_value in zip(sin2theta_values, polarisation_values)}
	sorted_keys = sorted(final_calibration.keys(), key=lambda sin2theta: sin2theta.nominal_value)
	
	n_points = len(final_calibration)
	
	graph_values_sin2theta = numpy.array([key.nominal_value for key in sorted_keys])
	graph_errors_sin2theta = numpy.array([key.std_dev for key in sorted_keys])
	graph_values_pol = numpy.array([final_calibration[key].nominal_value for key in sorted_keys])
	graph_errors_pol = numpy.array([final_calibration[key].std_dev for key in sorted_keys])
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
	
	output_file_path, root_directory = output_path.split(":")
	output_file = ROOT.TFile(output_file_path, "UPDATE")
	
	tools.write_object(output_file, graph_sin2theta_vs_pol, os.path.join(root_directory, "sin2theta_vs_pol"))
	tools.write_object(output_file, graph_pol_vs_sin2theta, os.path.join(root_directory, "pol_vs_sin2theta"))
	tools.write_object(output_file, graph_sin2theta_vs_pol_plus_sigma, os.path.join(root_directory, "sin2theta_vs_pol_plus_sigma"))
	tools.write_object(output_file, graph_sin2theta_vs_pol_minus_sigma, os.path.join(root_directory, "sin2theta_vs_pol_minus_sigma"))
	tools.write_object(output_file, graph_pol_plus_sigma_vs_sin2theta, os.path.join(root_directory, "pol_plus_sigma_vs_sin2theta"))
	tools.write_object(output_file, graph_pol_minus_sigma_vs_sin2theta, os.path.join(root_directory, "pol_minus_sigma_vs_sin2theta"))
	
	print "Saved outputs in {output_path}".format(output_path=output_path)


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
	
	parser.add_argument("-o", "--outputs", nargs="+",
	                    default=default_outputs,
	                    help="Output *.root file(s) and path(s) inside. Format: path/to/file.root:path/to/directory [Default: %(default)s]")
	
	args = parser.parse_args()
	
	sin2theta_values = list(numpy.arange(args.sin2theta_min, args.sin2theta_max+args.sin2theta_delta, args.sin2theta_delta))
	sin2theta_edges = list(numpy.arange(args.sin2theta_min-0.5*args.sin2theta_delta, args.sin2theta_max+args.sin2theta_delta, args.sin2theta_delta))
	
	for energy_distribution_up, energy_distribution_down, output_path in zip(
		args.energy_distributions_up,
		args.energy_distributions_down,
		args.outputs
	):
		get_calibration_curve(
				args.zfitter_output,
				energy_distribution_up,
				energy_distribution_down,
				sin2theta_values,
				sin2theta_edges,
				output_path
		)

