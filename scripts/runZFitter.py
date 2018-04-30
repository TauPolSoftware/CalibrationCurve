#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import fileinput
import numpy
import shutil
import os

import ROOT

import TauPolSoftware.CalibrationCurve.tools as tools


if __name__ == "__main__":
	
	parser = argparse.ArgumentParser(description="Run (modified) ZFitter. Obtaining P(s) and sigma(s) from ZFitter for different sin^2 theta_W and setting range and steps of energy for which the values should be calculated.")
	
	parser.add_argument("--sin2theta-min", type=float, default=0.200,
	                    help="Min. sin^2 theta_W value for scan. [Default: %(default)s]")
	parser.add_argument("--sin2theta-max", type=float, default=0.250,
	                    help="Max. sin^2 theta_W value for scan. [Default: %(default)s]")
	parser.add_argument("--sin2theta-delta", type=float, default=0.005,
	                    help="Sin^2 theta_W step size for scan. [Default: %(default)s]")
	
	parser.add_argument("--sqrts-min", type=float, default=80.0,
	                    help="Min. sqrt(s) value for scan. [Default: %(default)s]")
	parser.add_argument("--sqrts-max", type=float, default=110.0,
	                    help="Max. sqrt(s) value for scan. [Default: %(default)s]")
	parser.add_argument("--sqrts-delta", type=float, default=0.25,
	                    help="Sqrt(s) step size for scan. [Default: %(default)s]")
	
	parser.add_argument("-o", "--output", default="$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/data/zfitter.root",
	                    help="Output *.root file. [Default: %(default)s]")
	
	args = parser.parse_args()
	args.output = os.path.expandvars(args.output)
	
	# create an array for sin^2 theta_W values
	sin2theta_values = ["SINEFF={value}".format(value=value) for value in numpy.arange(args.sin2theta_min, args.sin2theta_max+args.sin2theta_delta, args.sin2theta_delta)]
	
	# create an array for sqrt(s) values
	sqrts_steps = (args.sqrts_max-args.sqrts_min)/args.sqrts_delta+1
	sqrts_values = list(numpy.arange(args.sqrts_min, args.sqrts_max+args.sqrts_delta, args.sqrts_delta))

	# starting the process for U and D quarks
	for quark in ["D", "U"]:

		# Copying files to substitute to ZFitter folder
		shutil.copyfile(
				os.path.expandvars("$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/zFitter/FilesToSubstitute/dizet6_42.f"),
				os.path.expandvars("$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/zFitter/dizet6_42.f")
		)
		shutil.copyfile(
				os.path.expandvars("$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/zFitter/FilesToSubstitute/zfusr6_42{quark}.f").format(quark=quark.lower()),
				os.path.expandvars("$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/zFitter/zfusr6_42.f")
		)

		# writing range of energy and steps into file
		for line in fileinput.input(os.path.expandvars("$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/zFitter/zfusr6_42.f"), inplace=True):
			print line.rstrip().replace("DO I = 1,560", "DO I = 1,{sqrts_steps}".format(sqrts_steps=sqrts_steps))
		for line in fileinput.input(os.path.expandvars("$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/zFitter/zfusr6_42.f"), inplace=True):
			print line.rstrip().replace("RS = 35.0+0.25*(I-1)", "RS = {sqrts_min}+{sqrts_delta}*(I-1)".format(sqrts_min=args.sqrts_min, sqrts_delta=args.sqrts_delta))

		# looping over all requested values for sin^2 theta_W
		for sin2theta_low, sin2theta_high in [(None, sin2theta_values[0])]+zip(sin2theta_values[:-1], sin2theta_values[1:]):
			print "{value} run: compiling ZFitter, running ZFitter".format(value=sin2theta_high)
		
			# setting names for output
			if sin2theta_low is None:
				for line in fileinput.input(os.path.expandvars("$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/zFitter/zfusr6_42.f"), inplace=True):
					print line.rstrip().replace("PolarizationAndXsecQuark{quark}_UNDEFINED".format(quark=quark), "PolarizationAndXsecQuark{quark}_{value}".format(quark=quark, value=sin2theta_high))
			else:
				for line in fileinput.input(os.path.expandvars("$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/zFitter/zfusr6_42.f"), inplace=True):
					print line.rstrip().replace("PolarizationAndXsecQuark{quark}_{value}".format(quark=quark, value=sin2theta_low), "PolarizationAndXsecQuark{quark}_{value}".format(quark=quark, value=sin2theta_high))

			# setting sin^2 theta_W value
			if sin2theta_low is None:
				for line in fileinput.input(os.path.expandvars("$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/zFitter/dizet6_42.f"), inplace=True):
					print line.rstrip().replace("SINEFF=0.200", sin2theta_values[0])
				print "(SINEFF=UNDEFINED to {value})".format(value=sin2theta_values[0])
			else:
				for line in fileinput.input(os.path.expandvars("$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/zFitter/dizet6_42.f"), inplace=True):
					print line.rstrip().replace(sin2theta_low, sin2theta_high)
				print "({value_low} to {value_high})".format(value_low=sin2theta_low, value_high=sin2theta_high)

			# compile ZFitter
			os.system(os.path.expandvars("cd $CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/zFitter && g77 -g  -fno-automatic -fdollar-ok -fno-backslash -finit-local-zero -fno-second-underscore -fugly-logint -ftypeless-boz  *.f -o zfitr642.exe"))

			# starting ZFitter
			os.system(os.path.expandvars("$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/zFitter/zfitr642.exe"))

	# Writing data into TFile
	output_file = ROOT.TFile(args.output, "RECREATE")

	for quark in ["D", "U"]:
		for sin2theta_value in sin2theta_values:
			tree=ROOT.TTree()
			tree.ReadFile("PolarizationAndXsecQuark{quark}_{value}.dat".format(quark=quark, value=sin2theta_value), "s:xsec:pol")
			tree.SetName("{quark} {value}".format(quark=quark.replace("D", "Down").replace("U", "Up"), value=sin2theta_value))
			tools.write_object(output_file, tree, "{quark}/{quark}{value}".format(quark=quark.replace("D", "Down").replace("U", "Up"), value=sin2theta_value.replace("=", "")))
			output_file.Write()
	output_file.Close()
	print "Safed outputs in\n\t{output_file}".format(output_file=args.output)

	#Deleting .dat files after they were written into the TFile
	for sin2theta_value in sin2theta_values:
		os.system("rm PolarizationAndXsecQuarkU_%s.dat" % sin2theta_value)
		os.system("rm PolarizationAndXsecQuarkD_%s.dat" % sin2theta_value)

