#!/usr/bin/env python

import os
import argparse
import ROOT
import math
import array



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--input-file",help="input file. [Default: %(default)s] ", action="store", default = 'madgraphlhe_tree_1M_50GeVCut.root')
    parser.add_argument("-r", "--integration-range",help="Integration range [Default: %(default)s] ",  type=str, action="store", default = '85,100')
    args = parser.parse_args()
    bin_list = [int(item) for item in args.integration_range.split(',')]
    
    def get_tree(path):
        input_file_path, tree_name = path.split(":")
        input_file = ROOT.TFile(input_file_path, "READ")
        tree = input_file.Get(tree_name)
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


    def get_integral(values):
        nom = sum(array.array("d", [x*y for x,y in zip(values[0],values[1])] ))
        denom   = sum(values[0])
        return nom/denom



    tr = get_tree(args.input_file+":lhetree");
    output_file = ROOT.TFile("output_"+args.input_file, "RECREATE")

    mass_bin_min = 50
    mass_bin_max = 150
    mass_bin_n =   70

    hist = ROOT.TH1F("hist","Z mass",mass_bin_n,mass_bin_min,mass_bin_max)    
    tr.Project("hist","zmass")
    neg_spin_ident = "spin < 0 && pdgid == 15 &&" 
    pos_spin_ident = "spin > 0 && pdgid == 15 &&"


    selection_list_m=([ neg_spin_ident + "  zmass >  " + str(i)+ " && zmass < " + str(j) for i,j in zip(get_binning(hist,0)[:-1],  get_binning(hist,0)[1:]) ])
    selection_list_p=([ pos_spin_ident + "  zmass >  " + str(i)+ " && zmass < " + str(j) for i,j in zip(get_binning(hist,0)[:-1],  get_binning(hist,0)[1:]) ])
    selected_plus= array.array("d",[tr.GetEntries(select_plus) for select_plus in selection_list_p])
    selected_minus= array.array("d",[tr.GetEntries(select_minus) for select_minus in selection_list_m])

    pol = array.array("d",[ 0 if  (a + b) == 0 else (a - b)/(a + b)  for a,b in zip(selected_plus, selected_minus)  ])
    ebin=array.array("d",[0.5*(i+j) for i,j in zip(get_binning(hist,0)[:-1],  get_binning(hist,0)[1:]) ])

    gr_pol= ROOT.TGraph(len(ebin),ebin,pol )
    gr_pol.SetName("polarization")
    gr_pol.SetTitle("Madgraph polarization")

    selection_list_m_overMZ=([  neg_spin_ident + "  zmass >  " + str(i)  for i in xrange(10,95)])
    selection_list_p_overMZ=([  pos_spin_ident + "  zmass >  " + str(i)  for i in xrange(10,95)])

    selected_plus_overMZ= array.array("d",[tr.GetEntries(select_plus) for select_plus in selection_list_p_overMZ])
    selected_minus_overMZ= array.array("d",[tr.GetEntries(select_minus) for select_minus in selection_list_m_overMZ])

    pol_overMZ= array.array("d", [0 if  (a + b) == 0 else (a - b)/(a + b)  for a,b in zip(selected_plus_overMZ, selected_minus_overMZ)  ])
    cut_value = array.array("d", [i for i in xrange(10,95)])

   
    gr_pol_overMZ= ROOT.TGraph(len(cut_value),cut_value,pol_overMZ )
    gr_pol_overMZ.SetName("av_polarization")
    gr_pol_overMZ.SetTitle("Integrated polarization with a mass cut (cut > M_z - x Axis)")
    gr_pol_overMZ.GetXaxis().SetTitle("cut > M_{z}");
    gr_pol_overMZ.GetXaxis().SetRange(1,100);
    gr_pol_overMZ.GetXaxis().SetLabelFont(42);
    gr_pol_overMZ.GetXaxis().SetLabelSize(0.035);
    gr_pol_overMZ.GetXaxis().SetTitleSize(0.035);
    gr_pol_overMZ.GetXaxis().SetTitleFont(42);
    gr_pol_overMZ.GetYaxis().SetTitle("<P_{#tau} >");


    mass_cut_min = bin_list[0]
    mass_cut_max = bin_list[1]
    mass_cut_bins = 50
    mass_selection = "zmass > " + str(mass_cut_min) + " && zmass< " + str(mass_cut_max)
    hist_xsec= ROOT.TH1F("hist_xsec","Integrated region of Z shape",mass_cut_bins,mass_cut_min,mass_cut_max)    
    tr.Project("hist_xsec","zmass", mass_selection)
 


    selection_list_m=([ neg_spin_ident + "  zmass >  " + str(i)+ " && zmass < " + str(j) for i,j in zip(get_binning(hist_xsec,0)[:-1],  get_binning(hist_xsec,0)[1:]) ])
    selection_list_p=([ pos_spin_ident + "  zmass >  " + str(i)+ " && zmass < " + str(j) for i,j in zip(get_binning(hist_xsec,0)[:-1],  get_binning(hist_xsec,0)[1:]) ])
    selected_plus= array.array("d",[tr.GetEntries(select_plus) for select_plus in selection_list_p])
    selected_minus= array.array("d",[tr.GetEntries(select_minus) for select_minus in selection_list_m])

    polarization = array.array("d",[ 0 if  (a + b) == 0 else (a - b)/(a + b)  for a,b in zip(selected_plus, selected_minus)  ])
    energy=array.array("d",[0.5*(i+j) for i,j in zip(get_binning(hist_xsec,0)[:-1],  get_binning(hist_xsec,0)[1:]) ])
    xsec = array.array("d", [ hist_xsec.GetBinContent(i) for i in xrange(1,hist_xsec.GetXaxis().GetNbins()+1) ])

    selection_negative= "spin < 0 && pdgid == 15 &&  " + mass_selection
    selection_positive= "spin > 0 && pdgid == 15 &&  " + mass_selection

    values=[]
    values.append(xsec)
    values.append(polarization)

    Neg_Pol = float(tr.GetEntries(selection_negative)) 
    Pos_Pol = float(tr.GetEntries(selection_positive))

    print "Countwise polarization (measured):  ", (Pos_Pol - Neg_Pol) / (Pos_Pol + Neg_Pol)
    print "Calculated polarization (expected):  ",  get_integral(values)
    gr_pol.Write()
    gr_pol_overMZ.Write()
    output_file.Write()
    output_file.Close()

 
