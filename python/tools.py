# -*- coding: utf-8 -*-

import array

import ROOT


def get_binning(root_histogram, axisNumber=0):
	axis = None
	if axisNumber == 0:
		axis = root_histogram.GetXaxis()
	elif axisNumber == 1:
		axis = root_histogram.GetYaxis()
	elif axisNumber == 2:
		axis = root_histogram.GetZaxis()
	return array.array("d", [axis.GetBinLowEdge(binIndex) for binIndex in xrange(1, axis.GetNbins()+2)])


def write_object(root_file, root_object, path):
	root_file.cd()
	root_directory = root_file
	for directory in path.split("/")[:-1]:
		if root_directory.Get(directory) == None:
			root_directory.mkdir(directory)
		root_directory = root_directory.Get(directory)
		root_directory.cd()
	root_object.Write(path.split("/")[-1], ROOT.TObject.kWriteDelete)
	root_file.cd()

