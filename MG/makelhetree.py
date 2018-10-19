#!/usr/bin/env python

import os
import ROOT
import pylhe
import math
from array import array


output_file = ROOT.TFile("output.root", "RECREATE")
output_tree = ROOT.TTree()
output_tree.SetName("lhetree")

pdgid = array( 'f', [ 0 ] )
px = array( 'f', [ 0 ] )
py = array( 'f', [ 0 ] )
pz = array( 'f', [ 0 ] )
energy = array( 'f', [ 0 ] )
mass = array( 'f', [ 0 ] )
zmass = array( 'f', [ 0 ] )
spin = array( 'f', [ 0 ] )


output_tree.Branch("px",px , "px/F")
output_tree.Branch("py",py , "py/F")
output_tree.Branch("pz",pz , "pz/F")
output_tree.Branch("energy",energy , "energy/F")
output_tree.Branch("mass",mass , "mass/F")
output_tree.Branch("zmass",zmass , "zmass/F")
output_tree.Branch("spin",spin , "spin/F")
output_tree.Branch("pdgid", pdgid, "pdgid/F")


h = ROOT.TH1F('invmass','Invariant Mass of Final State',150,0,175)
h.SetFillColor(38)

def invariant_mass(p1,p2):
    return math.sqrt(sum((1 if mu=='e' else -1)*(getattr(p1,mu)+getattr(p2,mu))**2 for mu in ['e','px','py','pz']))


for e in pylhe.readLHE('unweighted_events_80GeVCut.lhe'):
    h.Fill(invariant_mass(e.particles[-1],e.particles[-2]),e.eventinfo.weight)
    zmass[0]=invariant_mass(e.particles[-1],e.particles[-2]);
    for p in e.particles:
        pdgid[0] = getattr(p,'id')  
        px[0] = getattr(p,'px')
        py[0] = getattr(p,'py')
        pz[0] = getattr(p,'pz')
        energy[0] = getattr(p,'e')
        mass[0] = getattr(p,'m')
        spin[0] = getattr(p,'spin')
        output_tree.Fill()



output_tree.Write()
output_file.Write()
