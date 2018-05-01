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


if __name__ == "__main__":
	
	parser = argparse.ArgumentParser(description="Combine the data of up-type and down-type quarks from ZFitter and using the NLOPDF and calculate their errors.")
	
	parser.add_argument("--input-zfitter", default="$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/data/zfitter.root",
	                    help="Input *.root file from ZFitter containing up/down-type polarisations. [Default: %(default)s]")
	parser.add_argument("--input-pdf", default="$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/data/pfractions.root",
	                    help="Input *.root file from PDFs containing quark fractions. [Default: %(default)s]")
	
	parser.add_argument("--sin2theta-min", type=float, default=0.200,
	                    help="Min. sin^2 theta_W value for scan. [Default: %(default)s]")
	parser.add_argument("--sin2theta-max", type=float, default=0.250,
	                    help="Max. sin^2 theta_W value for scan. [Default: %(default)s]")
	parser.add_argument("--sin2theta-delta", type=float, default=0.005,
	                    help="Sin^2 theta_W step size for scan. [Default: %(default)s]")
	
	parser.add_argument("-o", "--output", default="$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/data/calibration.root",
	                    help="Output *.root file. [Default: %(default)s]")
	
	args = parser.parse_args()
	args.input_zfitter = os.path.expandvars(args.input_zfitter)
	args.input_pdf = os.path.expandvars(args.input_pdf)
	args.output = os.path.expandvars(args.output)
	
	input_file_pdf = ROOT.TFile(args.input_pdf, "READ")
	quark_fractions_tree = input_file_pdf.Get("Fractions/Fractions")
	
	input_file_zfitter = ROOT.TFile(args.input_zfitter, "READ")
	output_file = ROOT.TFile(args.output, "RECREATE")

	#Create a new Tree
	output_file.cd()
	output_tree = ROOT.TTree()

	#Create variables which are going to be written in the branches
	sin2theta_branch = numpy.zeros(1, dtype=float)
	energy_branch = numpy.zeros(1, dtype=float)
	xsec_branch = numpy.zeros(1, dtype=float)
	xsecerr_branch = numpy.zeros(1, dtype=float)
	pol_branch = numpy.zeros(1, dtype=float)
	polerr_branch = numpy.zeros(1, dtype=float)

	#Create a branch for each variable in the tree
	output_tree.Branch("sin2theta", sin2theta_branch, "sin2theta/D")
	output_tree.Branch("energy", energy_branch, "energy/D")
	output_tree.Branch("xsec", xsec_branch, "xsec/D")
	output_tree.Branch("xsecerr", xsecerr_branch, "xsecerr/D")
	output_tree.Branch("pol", pol_branch, "pol/D")
	output_tree.Branch("polerr", polerr_branch, "polerr/D")

	# create an array for sin^2 theta_W values
	sin2theta_values = list(numpy.arange(args.sin2theta_min, args.sin2theta_max+args.sin2theta_delta, args.sin2theta_delta))
	sin2theta_labels = ["{value:04}".format(value=int(value*1000)) for value in sin2theta_values]

	#loop over all values of sin^2 theta_W
	for sin2theta_value, sin2theta_label in zip(sin2theta_values, sin2theta_labels):
		
		sin2theta_branch[0] = sin2theta_value
	
		#Read in the relevant data from input
		down_values_tree = input_file_zfitter.Get("Down/Down{value}".format(value=sin2theta_label))
		up_values_tree = input_file_zfitter.Get("Up/Up{value}".format(value=sin2theta_label))

		##Calculate values for the variables and fill the branches with them	
		#loop over each entry
		assert (down_values_tree.GetEntries() == up_values_tree.GetEntries())
		assert (down_values_tree.GetEntries() == quark_fractions_tree.GetEntries())
		for entry in xrange(down_values_tree.GetEntries()):
			down_values_tree.GetEntry(entry)
			up_values_tree.GetEntry(entry)
			quark_fractions_tree.GetEntry(entry)
			assert (down_values_tree.energy == up_values_tree.energy)
			assert (down_values_tree.energy == quark_fractions_tree.energy)
		
			# Calculate ratios and corresponding errors of up-type and down-type quarks
			up = uncertainties.ufloat(quark_fractions_tree.up, quark_fractions_tree.uperr)
			down = uncertainties.ufloat(quark_fractions_tree.down, quark_fractions_tree.downerr)
			strange = uncertainties.ufloat(quark_fractions_tree.strange, quark_fractions_tree.strangeerr)
			charm = uncertainties.ufloat(quark_fractions_tree.charm, quark_fractions_tree.charmerr)
			bottom = uncertainties.ufloat(quark_fractions_tree.bottom, quark_fractions_tree.bottomerr)
			
			ratio_up = (up + charm) / (up + charm + down + strange + bottom)
			ratio_down = (down + strange + bottom) / (up + charm + down + strange + bottom)
			
			xsec_up = uncertainties.ufloat(up_values_tree.xsec, 0.0)
			xsec_down = uncertainties.ufloat(down_values_tree.xsec, 0.0)
			pol_up = uncertainties.ufloat(up_values_tree.pol, 0.0)
			pol_down = uncertainties.ufloat(down_values_tree.pol, 0.0)
			
			pol = (pol_up * ratio_up * xsec_up + pol_down * ratio_down * xsec_down) / (ratio_up * xsec_up + ratio_down * xsec_down)
			xsec = (xsec_up * (up + charm)) + (xsec_down * (down + strange + bottom))
			
			# fill branches
			energy_branch[0] = quark_fractions_tree.energy
			xsec_branch[0] = xsec.nominal_value
			xsecerr_branch[0] = xsec.std_dev
			pol_branch[0] = pol.nominal_value
			polerr_branch[0] = pol.std_dev
			
			#Fill the calculated data into the tree
			output_tree.Fill()
		
	#Write the tree into the Datafile
	output_file.cd()
	tools.write_object(output_file, output_tree, "calibration")

	#Close the files
	output_file.Close()
	input_file_zfitter.Close()
	input_file_pdf.Close()
	print "Saved outputs in\n\t{output_file}".format(output_file=args.output)

