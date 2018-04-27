#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import argparse

import ROOT

import TauPolSoftware.CalibrationCurve.tools as tools


if __name__ == "__main__":
	
	parser = argparse.ArgumentParser(description="Convert quark fractions as a function of the energy from *.dat to *.root.")
	
	parser.add_argument("-i", "--input", default="$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/pdf/FileWithIntegrals.dat",
	                    help="Input *.dat file. [Default: %(default)s]")
	parser.add_argument("-o", "--output", default="$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/data/pfractions.root",
	                    help="Output *.root file. [Default: %(default)s]")
	
	args = parser.parse_args()
	args.input = os.path.expandvars(args.input)
	args.output = os.path.expandvars(args.output)

	#Storing fraction values of quarks for energies in data.root
	output_file = ROOT.TFile(args.output, "RECREATE")
	tree = ROOT.TTree()
	tree.ReadFile(args.input, "energy:down:errd:up:erru:strange:errs:charm:errc:bottom:errb")
	tree.SetName("Fractions")
	tools.write_object(output_file, tree, "Fractions/Fractions")
	output_file.Write()
	output_file.Close()
	print "Converted\n\t{input_file}\nto\n\t{output_file}".format(input_file=args.input, output_file=args.output)

