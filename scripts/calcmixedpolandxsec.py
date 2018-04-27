#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import math
import numpy
import os

import ROOT

import TauPolSoftware.CalibrationCurve.tools as tools


#Function which calculates the error for an expression of two variables
def calcerror(a,ae,b,be,string):
	if string == "sum":
		return math.sqrt(pow(ae,2)+pow(be,2))
	if string == "product":
		return math.sqrt(pow(b*ae,2)+pow(a*be,2))
	if string == "ratio":
		return math.sqrt(pow(ae/b,2)+pow(a*be/pow(b,2),2))


if __name__ == "__main__":
	
	parser = argparse.ArgumentParser(description="Combine the data of up-type and down-type quarks from ZFitter and using the NLOPDF and calculate their errors.")
	
	parser.add_argument("--input-zfitter", default="$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/data/zfitter.root",
	                    help="Input *.root file from ZFitter containing up/down-type polarisations. [Default: %(default)s]")
	parser.add_argument("--input-pdf", default="$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/data/zfitter.root",
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

	# create an array for sin^2 theta_W values
	sin2theta_values = ["SINEFF={value}".format(value=value) for value in numpy.arange(args.sin2theta_min, args.sin2theta_max+args.sin2theta_delta, args.sin2theta_delta)]

	#loop over all values of sin^2 theta_W
	for sin2theta_value in sin2theta_values:
	
		#Read in the relevant data from input
		down_values_tree = input_file_zfitter.Get("Down/Down%s"%sin2theta_value.replace("=",""))
		up_values_tree = input_file_zfitter.Get("Up/Up%s"%sin2theta_value.replace("=",""))

		#Create a new Tree
		output_file.cd()
		output_tree = ROOT.TTree()
		output_tree.SetName("Combined {value}".format(value=sin2theta_value))

		#Create variables which are going to be written in the branches
		energy = numpy.zeros(1,dtype=float)
		xsec = numpy.zeros(1,dtype=float)
		xsecerr = numpy.zeros(1,dtype=float)
		pol = numpy.zeros(1,dtype=float)
		polerr = numpy.zeros(1,dtype=float)

		#Create a branch for each variable in the tree
		output_tree.Branch("energy", energy, "energy/D")
		output_tree.Branch("xsec", xsec, "xsec/D")
		output_tree.Branch("xsecerr", xsecerr, "xsecerr/D")
		output_tree.Branch("pol", pol, "pol/D")
		output_tree.Branch("polerr", polerr, "polerr/D")

		##Calculate values for the variables and fill the branches with them	
		#loop over each entry
		assert (down_values_tree.GetEntries() == up_values_tree.GetEntries())
		assert (down_values_tree.GetEntries() == quark_fractions_tree.GetEntries())
		for entry in range(down_values_tree.GetEntries()):
			down_values_tree.GetEntry(entry)
			up_values_tree.GetEntry(entry)
			quark_fractions_tree.GetEntry(entry)
		
			#Copy energy
			energy[0] = down_values_tree.s

			#Calculate ratios and corresponding errors of up-type and down-type quarks
			rU = (quark_fractions_tree.up+quark_fractions_tree.charm)/(quark_fractions_tree.up+quark_fractions_tree.charm+quark_fractions_tree.down+quark_fractions_tree.bottom+quark_fractions_tree.strange)
			rD = 1-rU
			rerr = calcerror(quark_fractions_tree.up+quark_fractions_tree.charm,math.sqrt(pow(quark_fractions_tree.erru,2)+pow(quark_fractions_tree.errc,2)),quark_fractions_tree.up+quark_fractions_tree.charm+quark_fractions_tree.down+quark_fractions_tree.bottom+quark_fractions_tree.strange,math.sqrt(pow(quark_fractions_tree.erru,2)+pow(quark_fractions_tree.errc,2)+pow(quark_fractions_tree.errd,2)+pow(quark_fractions_tree.errb,2)+pow(quark_fractions_tree.errs,2)),"ratio")
		
			#Calculate combined polarisation and corresponding errors
			denom = rU*up_values_tree.xsec+rD*down_values_tree.xsec
			pol[0] = (rU*up_values_tree.pol*up_values_tree.xsec+rD*down_values_tree.pol*down_values_tree.xsec)/denom
			deriv1 = (up_values_tree.pol*up_values_tree.xsec)/denom-(up_values_tree.pol*up_values_tree.xsec*rU)*(up_values_tree.xsec-down_values_tree.xsec)/pow(denom,2)
			deriv2 = -(down_values_tree.pol*down_values_tree.xsec)/denom-(down_values_tree.pol*down_values_tree.xsec*rD)*(up_values_tree.xsec-down_values_tree.xsec)/pow(denom,2)
			polerr[0] = math.sqrt(pow(deriv1,2)+pow(deriv2,2))*rerr

			#Calculate combined cross-section and corresponding errors
			xsec[0] = up_values_tree.xsec*(quark_fractions_tree.up+quark_fractions_tree.charm)+down_values_tree.xsec*(quark_fractions_tree.down+quark_fractions_tree.strange+quark_fractions_tree.bottom)
			xsecerr[0] = math.sqrt(pow(up_values_tree.xsec,2)*(pow(quark_fractions_tree.erru,2)+pow(quark_fractions_tree.errc,2))+pow(down_values_tree.xsec,2)*(pow(quark_fractions_tree.errd,2)+pow(quark_fractions_tree.errs,2)+pow(quark_fractions_tree.errb,2)))
		
			#Fill the calculated data into the tree
			output_tree.Fill()

		#Write the tree into the Datafile
		output_file.cd()
		tools.write_object(output_file, output_tree, "Combined/Combined{value}".format(value=sin2theta_value.replace("=","")))

	#Close the files
	output_file.Close()
	input_file_zfitter.Close()
	input_file_pdf.Close()

