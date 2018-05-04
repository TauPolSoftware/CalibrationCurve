# -*- coding: utf-8 -*-

import array
import multiprocessing
import time

import ROOT

import TauPolSoftware.CalibrationCurve.progressiterator as pi


def parallelize(function, arguments_list, n_processes=1, description=None):
	if n_processes <= 1:
		results = []
		for arguments in pi.ProgressIterator(arguments_list, description=(description if description else "calling "+str(function))):
			results.append(function(arguments))
		return results
	else:
		pool = multiprocessing.Pool(processes=max(1, min(n_processes, len(arguments_list))))
		results = pool.map_async(function, arguments_list, chunksize=1)
		n_tasks = len(arguments_list)
		left = n_tasks-1
		progress_iterator = pi.ProgressIterator(range(n_tasks), description=(description if description else "calling "+str(function)))
		progress_iterator.next()
		while (True):
			ready = results.ready()
			remaining = results._number_left
			if ready or (remaining < left):
				for i in range(left-remaining):
					progress_iterator.next()
				left = remaining
			if ready:
				break
			time.sleep(1.0)
		returnvalue = results.get(9999999)
		pool.close() # necessary to actually terminate the processes
		pool.join()  # without these two lines, they happen to live until the whole program terminates
		return returnvalue


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

