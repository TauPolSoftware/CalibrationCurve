#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import numpy
import string
import os

import ROOT

import TauPolSoftware.CalibrationCurve.tools as tools


if __name__ == "__main__":
	
	parser = argparse.ArgumentParser(description="Run (modified) ZFitter. Obtaining P(sqrt s) and sigma(sqrt s) from ZFitter for different sin^2 theta_W and setting range and steps of energy for which the values should be calculated.")
	
	parser.add_argument("--sin2theta-min", type=float, default=0.150,
	                    help="Min. sin^2 theta_W value for scan. [Default: %(default)s]")
	parser.add_argument("--sin2theta-max", type=float, default=0.300,
	                    help="Max. sin^2 theta_W value for scan. [Default: %(default)s]")
	parser.add_argument("--sin2theta-delta", type=float, default=0.0025,
	                    help="Sin^2 theta_W step size for scan. [Default: %(default)s]")
	
	parser.add_argument("--energy-min", type=float, default=10.0,
	                    help="Min. sqrt(s) value for scan. [Default: %(default)s]")
	parser.add_argument("--energy-max", type=float, default=200.0,
	                    help="Max. sqrt(s) value for scan. [Default: %(default)s]")
	parser.add_argument("--energy-delta", type=float, default=0.25,
	                    help="Sqrt(s) step size for scan. [Default: %(default)s]")
	
	parser.add_argument("-o", "--output", default="$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/data/zfitter.root",
	                    help="Output *.root file. [Default: %(default)s]")
	
	args = parser.parse_args()
	args.output = os.path.expandvars(args.output)
	
	# create an array for sin^2 theta_W values
	sin2theta_values = list(numpy.arange(args.sin2theta_min, args.sin2theta_max+args.sin2theta_delta, args.sin2theta_delta))
	sin2theta_labels = ["{value:04}".format(value=int(value*1000)) for value in sin2theta_values]
	
	# create an array for sqrt(s) values
	energy_steps = (args.energy_max-args.energy_min)/args.energy_delta+1
	energy_values = list(numpy.arange(args.energy_min, args.energy_max+args.energy_delta, args.energy_delta))

	# load templates for replacements in fortran code
	dizet_template = None
	with open(os.path.expandvars("$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/zFitter/FilesToSubstitute/dizet6_42.f")) as dizet_file:
		dizet_template = string.Template(dizet_file.read())
	
	output_file = ROOT.TFile(args.output, "RECREATE")
	
	# starting the process for U and D quarks
	for quark in ["D", "U"]:
		output_tree = ROOT.TTree()
		output_tree.SetName("zfitter_{quark}".format(quark=quark.replace("D", "down").replace("U", "up")))
		
		# load templates for replacements in fortran code
		zfusr_template = None
		with open(os.path.expandvars("$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/zFitter/FilesToSubstitute/zfusr6_42{quark}.f").format(quark=quark.lower())) as zfusr_file:
			zfusr_template = string.Template(zfusr_file.read())

		# looping over all requested values for sin^2 theta_W
		for sin2theta_value, sin2theta_label in zip(sin2theta_values, sin2theta_labels):
			print "sin^2 theta_W={value} run: compiling ZFitter, running ZFitter".format(value=sin2theta_value)
			
			# replacements in fortran code
			dizet_code = dizet_template.safe_substitute(
					replacement_sin2theta=str(sin2theta_value)
			)
			with open(os.path.expandvars("$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/zFitter/dizet6_42.f"), "w") as dizet_file:
				dizet_file.write(dizet_code)
			
			zfusr_code = zfusr_template.safe_substitute(
					replacement_sin2theta_label=sin2theta_label,
					replacement_n_energy_values=str(len(energy_values)),
					replacement_energy_min=str(args.energy_min),
					replacement_energy_delta=str(args.energy_delta)
			)
			with open(os.path.expandvars("$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/zFitter/zfusr6_42.f"), "w") as zfusr_file:
				zfusr_file.write(zfusr_code)
			
			# compile ZFitter
			os.system(os.path.expandvars("rm $CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/zFitter/zfitr642.exe"))
			os.system(os.path.expandvars("cd $CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/zFitter && g77 -g  -fno-automatic -fdollar-ok -fno-backslash -finit-local-zero -fno-second-underscore -fugly-logint -ftypeless-boz *.f -o zfitr642.exe"))

			# starting ZFitter
			os.system(os.path.expandvars("$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/zFitter/zfitr642.exe"))
			
			# add sin^2 theta_W column
			zfitter_dat_filename = "PolarizationAndXsecQuark{quark}_{value}.dat".format(quark=quark, value=sin2theta_label)
			zfitter_output = numpy.genfromtxt(fname=zfitter_dat_filename)
			zfitter_output = numpy.concatenate((zfitter_output, numpy.full((zfitter_output.shape[0], 1), sin2theta_value)), axis=1)
			numpy.savetxt(zfitter_dat_filename, zfitter_output)

			# Writing data into tree
			output_tree.ReadFile(zfitter_dat_filename, "energy:xsec:pol:sin2theta")
			
			#Deleting .dat files after they were written into the TFile
			os.system("rm PolarizationAndXsecQuark{quark}_{value}.dat".format(quark=quark, value=sin2theta_label))
		
		# save tree
		tools.write_object(output_file, output_tree, output_tree.GetName())
		
		# fill histogram
		output_tree.Draw("pol:sin2theta:energy>>{tree_name}_pol_vs_sin2theta_vs_energy({energy_bins},{energy_low},{energy_high},{sin2theta_bins},{sin2theta_low},{sin2theta_high})".format(
				tree_name = output_tree.GetName(),
				energy_bins = len(energy_values),
				energy_low = (args.energy_min - (args.energy_delta/2.0)),
				energy_high = (args.energy_max + (args.energy_delta/2.0)),
				sin2theta_bins = len(sin2theta_values),
				sin2theta_low = (args.sin2theta_min - (args.sin2theta_delta/2.0)),
				sin2theta_high = (args.sin2theta_max + (args.sin2theta_delta/2.0))
		), "", "prof goff")
	
	output_file.Write()
	output_file.Close()
	print "Saved outputs in\n\t{output_file}".format(output_file=args.output)

