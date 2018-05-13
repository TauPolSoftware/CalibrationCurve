
#!/usr/bin/env python

import datetime
import hashlib
import numpy
import os

import ROOT

import TauPolSoftware.CalibrationCurve.tools as tools

# the calculations here use the uncertainties package for the error propagation
# use <return value>.nominal_value to retrive the central value
# http://uncertainties-python-package.readthedocs.io/en/latest/user_guide.html
import TauPolSoftware.CalibrationCurve.uncertainties.uncertainties as uncertainties


class CalibrationCurve(object):

	def __init__(self, zfitter_output_path, energy_histogram_up_path, energy_histogram_down_path, sin2theta_edges, sin2theta_mc):
		self.zfitter_output_path = zfitter_output_path
		self.sin2theta_edges = sin2theta_edges
	
		self.energy_histogram_up = self._get_histogram(energy_histogram_up_path)
		self.energy_histogram_down = self._get_histogram(energy_histogram_down_path)
	
		sin2theta_mc_edges = [max([edge for edge in sin2theta_edges if edge < sin2theta_mc]), min([edge for edge in sin2theta_edges if edge > sin2theta_mc])]
		self.xsec_mc_histogram_up = self._get_zfitter_output_histogram(sin2theta_mc_edges[0], sin2theta_mc_edges[1], "up", "xsec")
		self.xsec_mc_histogram_down = self._get_zfitter_output_histogram(sin2theta_mc_edges[0], sin2theta_mc_edges[1], "down", "xsec")
	
		calibration_central_values = self._get_calibration_central_values()
	
		# no uncertainties implemented yet
		self.final_calibration = {uncertainties.ufloat(sin2theta, 0.0) : uncertainties.ufloat(polarisation, 0.0) for sin2theta, polarisation in calibration_central_values}

	def save_calibration_curves(self, output_path):
		sorted_keys = sorted(self.final_calibration.keys(), key=lambda sin2theta: sin2theta.nominal_value)
		n_points = len(self.final_calibration)
	
		graph_values_sin2theta = numpy.array([key.nominal_value for key in sorted_keys])
		graph_errors_sin2theta = numpy.array([key.std_dev for key in sorted_keys])
		graph_values_pol = numpy.array([self.final_calibration[key].nominal_value for key in sorted_keys])
		graph_errors_pol = numpy.array([self.final_calibration[key].std_dev for key in sorted_keys])
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

	def _get_histogram(self, path):
		input_file_path, histogram_path = path.split(":")
		input_file = ROOT.TFile(input_file_path, "OPEN")
		histogram = input_file.Get(histogram_path)
		histogram.SetDirectory(0)
		input_file.Close()
		return histogram

	def _get_zfitter_output_histogram(self, sin2theta_min, sin2theta_max, quark_type, quantity):
		energy_binning_histogram = self.energy_histogram_up if quark_type == "up" else self.energy_histogram_down
		zfitter_tree = ROOT.TChain("zfitter_{quark_type}".format(quark_type=quark_type))
		zfitter_tree.Add(self.zfitter_output_path)
	
		histogram_name = "zfitter_{quantity}_{quark_type}_".format(quantity=quantity, quark_type=quark_type)+hashlib.md5("".join([str(item) for item in [self.zfitter_output_path, sin2theta_min, sin2theta_max, energy_binning_histogram, quark_type, quantity, datetime.datetime.now()]])).hexdigest()
		binning = tools.get_binning(energy_binning_histogram)
		histogram = ROOT.TProfile(histogram_name, histogram_name, len(binning)-1, binning)
	
		zfitter_tree.Project(histogram_name, "{quantity}:energy".format(quantity=quantity), "(sin2theta>={sin2theta_min})*(sin2theta<{sin2theta_max})".format(
				sin2theta_min=sin2theta_min,
				sin2theta_max=sin2theta_max
		), "prof goff")
	
		histogram = ROOT.gDirectory.Get(histogram_name).ProjectionX() # projection to convert into TH1
		return histogram

	def _get_calibration_central_values(self):
		calibration_central_values = []
		for sin2theta_min, sin2theta_max in zip(self.sin2theta_edges[:-1], self.sin2theta_edges[1:]):
			sin2theta_value = float((sin2theta_min + sin2theta_max) / 2.0)
			calibration_central_values.append((sin2theta_value, self._calculate_polarisation(sin2theta_min, sin2theta_max)))
		return calibration_central_values

	def _calculate_polarisation(self, sin2theta_min, sin2theta_max):
		polarisation_histogram_up = self._get_zfitter_output_histogram(sin2theta_min, sin2theta_max, "up", "pol")
		polarisation_histogram_down = self._get_zfitter_output_histogram(sin2theta_min, sin2theta_max, "down", "pol")
		xsec_histogram_up = self._get_zfitter_output_histogram(sin2theta_min, sin2theta_max, "up", "xsec")
		xsec_histogram_down = self._get_zfitter_output_histogram(sin2theta_min, sin2theta_max, "down", "xsec")
		
		xsec_histogram_up.Divide(self.xsec_mc_histogram_up)
		xsec_histogram_up.Multiply(self.energy_histogram_up)
		xsec_histogram_down.Divide(self.xsec_mc_histogram_down)
		xsec_histogram_down.Multiply(self.energy_histogram_down)
		
		polarisation_histogram_up.Multiply(xsec_histogram_up)
		polarisation_histogram_down.Multiply(xsec_histogram_down)
	
		integral_polarisation_energy_xsec_up = polarisation_histogram_up.Integral()
		integral_polarisation_energy_xsec_down = polarisation_histogram_down.Integral()
	
		integral_energy_xsec_up = xsec_histogram_up.Integral()
		integral_energy_xsec_down = xsec_histogram_down.Integral()
	
		numerator = (integral_polarisation_energy_xsec_up + integral_polarisation_energy_xsec_down)
		denominator = (integral_energy_xsec_up + integral_energy_xsec_down)
		polarisation = 0.0
		if denominator != 0.0:
			polarisation = numerator / denominator
		return polarisation

