#!/usr/bin/env python

import os
import argparse
import ROOT
import math
import array



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--input-file",help="input file. [Default: %(default)s] ", action="store", default = 'histogram_MadGraph_thomas.root')
    args = parser.parse_args()
   
    def get_histogram(path):
        input_file_path, histogram_path = path.split(":")
        input_file = ROOT.TFile(input_file_path, "OPEN")
        histogram = input_file.Get(histogram_path)
        histogram.SetDirectory(0)
        input_file.Close()
        return histogram

    def get_center_binning(root_histogram, axisNumber=0):
        axis = None
        if axisNumber == 0:
            axis = root_histogram.GetXaxis()
        elif axisNumber == 1:
            axis = root_histogram.GetYaxis()
        elif axisNumber == 2:
            axis = root_histogram.GetZaxis()
        return array.array("d", [axis.GetBinCenter(binIndex) for binIndex in xrange(1, axis.GetNbins()+1)])

    def get_content(root_histogram, axisNumber=0):
        axis = None
        if axisNumber == 0:
            axis = root_histogram.GetXaxis()
        elif axisNumber == 1:
            axis = root_histogram.GetYaxis()
        elif axisNumber == 2:
            axis = root_histogram.GetZaxis()
        return array.array("d", [root_histogram.GetBinContent(binIndex) for binIndex in xrange(1, axis.GetNbins()+2)])
    histo_plus = get_histogram(args.input_file+":pos");
    histo_minus = get_histogram(args.input_file+":neg");

    pol = array.array("d",[ 0 if  (a + b) == 0 else (a - b)/(a + b)  for a,b in zip(get_content(histo_plus,0)[:-1], get_content(histo_minus,0)[:-1])  ])
    energy = get_center_binning(histo_plus,0)


    print energy.index(91.25), pol[energy.index(91.25)]
    gr_pol= ROOT.TGraph(len(energy),energy,pol )
    gr_pol.SetName("polarization")
    gr_pol.SetTitle("DY CMS Madgrgaph polarization")

    gr_pol.Draw()
