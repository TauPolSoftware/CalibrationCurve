#!/usr/bin/env python

import os
import argparse
import ROOT
import math
import array




    
    def get_tree(path):
        input_file_path, tree_name = path.split(":")
        input_file = ROOT.TFile(input_file_path, "READ")
        tree = input_file.Get(tree_name)
        tree.GetEntry(0)
        tree.SetDirectory(0)
        input_file.Close()
        return tree
    
    def get_binning(root_histogram, axisNumber=0):
        axis = None
        if axisNumber == 0:
            axis = root_histogram.GetXaxis()
        elif axisNumber == 1:
            axis = root_histogram.GetYaxis()
        elif axisNumber == 2:
            axis = root_histogram.GetZaxis()
        return array.array("d", [axis.GetBinLowEdge(binIndex) for binIndex in xrange(1, axis.GetNbins()+2)])

    def get_histogram(path):
        input_file_path, histogram_path = path.split(":")
        input_file = ROOT.TFile(input_file_path, "OPEN")
        histogram = input_file.Get(histogram_path)
        histogram.SetDirectory(0)
        input_file.Close()
        return histogram

    def get_integral(values):
        nom = sum(map(lambda n1,n2: n1*n2,values[0],values[1]))
        denom   = sum(values[0])
        return nom/denom


    path="tree_calc.root:tree_ave"
    input_file_path, tree_name = path.split(":")
    input_file = ROOT.TFile(input_file_path, "READ")
    tree = input_file.Get(tree_name)

    energy_cut_min=40.
    energy_cut_max=200.
    xsection=[]
    polarization=[]
    energy=[]
    values=[]
    
    s2tl=[]
    apol=[]
    list_size=1#len(s2tl)
    for entry in xrange(tree.GetEntries()):
        tree.GetEntry(entry) 
        if tree.energy>= energy_cut_min and tree.energy<=energy_cut_max:
            if tree.sin2theta not in s2tl:
                s2tl.append(tree.sin2theta) 
                
            xsection.append(tree.xsec)
            polarization.append(tree.pol)
            energy.append(tree.energy)
                
            if len(s2tl)!=list_size:
                print list_size, len(s2tl)
                list_size +=1
                values.append(xsection)
                values.append(polarization)
                values.append(energy)
            
                apol.append(get_integral(values))
                del xsection[:]
                del polarization[:]
                del energy[:]
                del values [:]
                    
    for entry in xrange(tree.GetEntries()):
        tree.GetEntry(entry) 
        if tree.energy>= energy_cut_min and tree.energy<=energy_cut_max:
            if tree.sin2theta  == s2tl[-1:]:
                xsection.append(tree.xsec)
                polarization.append(tree.pol)
                energy.append(tree.energy)

    values.append(xsection)
    values.append(polarization)
    values.append(energy)
    apol.append(get_integral(values))

    print polarization
    average_polarization= array.array("d", [ i  for i in apol ])
    sw2= array.array("d", [ i  for i in s2tl ])
    print sw2
    print len(s2tl), len(apol)

    CalibrationCurve_graph= ROOT.TGraph(len(sw2),sw2,average_polarization )
    CalibrationCurve_graph.Draw()
