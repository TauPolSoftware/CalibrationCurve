#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import glob
import numpy
import os
import string
import tempfile

import ROOT

import TauPolSoftware.CalibrationCurve.tools as tools


def get_zfitter_executable(arguments):
	quark_type = arguments[0]
	sin2theta_value = arguments[1]
	sin2theta_label = arguments[2]
	n_energy_values = arguments[3]
	energy_min = arguments[4]
	energy_delta = arguments[5]
	
	tmp_dir = tempfile.mkdtemp(prefix="zfitter_{quark_type}_{sin2theta_label}_".format(quark_type=quark_type, sin2theta_label=sin2theta_label))
	executable = os.path.join(tmp_dir, "zfitr642.exe")
	
	dizet_template = None
	with open(os.path.expandvars("$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/zFitter/FilesToSubstitute/dizet6_42.f")) as dizet_file:
		dizet_template = string.Template(dizet_file.read())
	
	dizet_code = dizet_template.safe_substitute(
			replacement_sin2theta=str(sin2theta_value)
	)
	
	with open(os.path.expandvars("$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/zFitter/dizet6_42.f"), "w") as dizet_file:
		dizet_file.write(dizet_code)
	
	zfusr_template = None
	with open(os.path.expandvars("$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/zFitter/FilesToSubstitute/zfusr6_42{quark_type}.f").format(quark_type=quark_type.lower())) as zfusr_file:
		zfusr_template = string.Template(zfusr_file.read())
	
	zfusr_code = zfusr_template.safe_substitute(
			replacement_sin2theta_label=sin2theta_label,
			replacement_n_energy_values=n_energy_values,
			replacement_energy_min=energy_min,
			replacement_energy_delta=energy_delta
	)
	
	with open(os.path.expandvars("$CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/zFitter/zfusr6_42.f"), "w") as zfusr_file:
		zfusr_file.write(zfusr_code)
	
	# compile ZFitter
	os.system(os.path.expandvars("cd $CMSSW_BASE/src/TauPolSoftware/CalibrationCurve/zFitter && g77 -g -fno-automatic -fdollar-ok -fno-backslash -finit-local-zero -fno-second-underscore -fugly-logint -ftypeless-boz *.f -o {executable}".format(executable=executable)))
	
	return [executable, quark_type, sin2theta_value, sin2theta_label]


def run_zfitter(arguments):
	executable = arguments[0]
	quark_type = arguments[1]
	sin2theta_value = arguments[2]
	sin2theta_label = arguments[3]
	
	print "sin^2 theta_W={value} run...".format(value=sin2theta_value)
	
	# run ZFitter
	tmp_dir = os.path.dirname(executable)
	tmp_executable = os.path.basename(executable)
	os.system("cd {tmp_dir} && ./{executable}".format(tmp_dir=tmp_dir, executable=tmp_executable))
	
	# add sin^2 theta_W column
	zfitter_dat_filename = os.path.join(tmp_dir, "PolarizationAndXsecQuark{quark_type}_{value}.dat".format(quark_type=quark_type, value=sin2theta_label))
	zfitter_output = numpy.genfromtxt(fname=zfitter_dat_filename)
	zfitter_output = numpy.concatenate((zfitter_output, numpy.full((zfitter_output.shape[0], 1), sin2theta_value)), axis=1)
	numpy.savetxt(zfitter_dat_filename, zfitter_output)
	
	return {quark_type : zfitter_dat_filename}


def collect_zfitter_outputs(zfitter_outputs, args):
	
	output_file = ROOT.TFile(args.output, "RECREATE")
	
	for quark_type, tmp_zfitter_outputs in zfitter_outputs.iteritems():
		# fill tree
		output_tree = ROOT.TTree()
		output_tree.SetName("zfitter_{quark_type}".format(quark_type=quark_type.replace("D", "down").replace("U", "up")))
		for zfitter_output in tmp_zfitter_outputs:
			output_tree.ReadFile(zfitter_output, "energy:xsec:pol:sin2theta")
			os.system("rm -r {zfitter_output}".format(zfitter_output=os.path.dirname(zfitter_output)))
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

	parser.add_argument("-n", "--n-processes", type=int, default=1,
	                    help="Number of (parallel) processes. [Default: %(default)s]")
	
	args = parser.parse_args()
	args.output = os.path.expandvars(args.output)
	
	sin2theta_values = list(numpy.arange(args.sin2theta_min, args.sin2theta_max+args.sin2theta_delta, args.sin2theta_delta))
	sin2theta_labels = ["{value:04}".format(value=int(value*1000)) for value in sin2theta_values]
	
	energy_steps = (args.energy_max-args.energy_min)/args.energy_delta+1
	energy_values = list(numpy.arange(args.energy_min, args.energy_max+args.energy_delta, args.energy_delta))
	
	quark_types = ["D", "U"]
	
	get_zfitter_executable_args = [[
			quark_type,
			sin2theta_value,
			"{value:04}".format(value=int(sin2theta_value*1000)),
			str(len(energy_values)),
			str(args.energy_min),
			str(args.energy_delta),
	] for quark_type in quark_types for sin2theta_value in sin2theta_values]
	
	run_zfitter_args = tools.parallelize(get_zfitter_executable, get_zfitter_executable_args, n_processes=1, description="Compile ZFitter executables")
	tmp_zfitter_outputs = tools.parallelize(run_zfitter, run_zfitter_args, n_processes=args.n_processes, description="Run ZFitter")
	
	zfitter_outputs = {}
	for tmp_zfitter_output in tmp_zfitter_outputs:
		for quark_type, zfitter_output in tmp_zfitter_output.iteritems():
			zfitter_outputs.setdefault(quark_type, []).append(zfitter_output)
	collect_zfitter_outputs(zfitter_outputs, args)

