
#!/usr/bin/env python

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

