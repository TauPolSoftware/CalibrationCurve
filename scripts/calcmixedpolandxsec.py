#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ROOT
import os
import math
import numpy as np

import TauPolSoftware.CalibrationCurve.tools as tools


#Function which calculates the error for an expression of two variables
def calcerror(a,ae,b,be,string):
    if string == "sum":
        return math.sqrt(pow(ae,2)+pow(be,2))
    if string == "product":
        return math.sqrt(pow(b*ae,2)+pow(a*be,2))
    if string == "ratio":
        return math.sqrt(pow(ae/b,2)+pow(a*be/pow(b,2),2))

""" Implemented in writequarkfractionstodata.py
#Storing fraction values of quarks for energies in data.root
f=ROOT.TFile("../data/data.root","UPDATE")
tree=ROOT.TTree()
tree.ReadFile("../pdf/FileWithIntegrals.dat","energy:down:errd:up:erru:strange:errs:charm:errc:bottom:errb")
tree.SetName("Fractions")
tools.write_object(f,tree,"Fractions/Fractions")
f.Write()
f.Close()
"""

#left end, right end, stepsize and number of steps for sin2T; create an array for sin2T for the values (has to be the same as in main.py)
lendsin2T=0.200
rendsin2T=0.250
stepsin2T=0.005
nstepsin2T=(rendsin2T-lendsin2T)/stepsin2T
sineff=[]

#Create an array of strings containing the values of sin2T
for i in range(int(nstepsin2T+2)):
    sineff.append("SINEFF=%s"%(lendsin2T+i*stepsin2T))


##Combine the data of up-type and down-type quarks from ZFitter and using the NLOPDF and calculate their errors
#Open the TFile (with the data from ZFitter and NLOPDF)
Datafile=ROOT.TFile("../data/data.root","UPDATE")

#loop over all values of sin2T
for i in range(len(sineff)):

	#Create a new Tree
	newtree=ROOT.TTree()
	newtree.SetName("Combined %s"%sineff[i])

	#Create variables which are going to be written in the branches
	energy=np.zeros(1,dtype=float)
	xsec=np.zeros(1,dtype=float)
	xsecerr=np.zeros(1,dtype=float)
	pol=np.zeros(1,dtype=float)
	polerr=np.zeros(1,dtype=float)

	#Create a branch for each variable in the tree
	newtree.Branch("energy",energy,"Energy/D")
	newtree.Branch("xsec",xsec,"Crosssection/D")
	newtree.Branch("xsecerr",xsecerr,"Crosssectionerr/D")
	newtree.Branch("pol",pol,"Polarization/D")
	newtree.Branch("polerr",polerr,"Polarizationerr/D")
	
	#Read in the relevant data from Datafile
	Downvals=Datafile.Get("Down/Down%s"%sineff[i].replace("=",""))
	Upvals=Datafile.Get("Up/Up%s"%sineff[i].replace("=",""))
	Qarks=Datafile.Get("Fractions/Fractions")

	##Calculate values for the variables and fill the branches with them	
	#loop over each entry
	for n in range(Downvals.GetEntries()):
		Downvals.GetEntry(n)
		Upvals.GetEntry(n)
		Qarks.GetEntry(n)
		
		#Copy energy
		energy[0]=Downvals.s

		#Calculate ratios and corresponding errors of up-type and down-type quarks
		rU=(Qarks.up+Qarks.charm)/(Qarks.up+Qarks.charm+Qarks.down+Qarks.bottom+Qarks.strange)
		rD=1-rU
		rerr=calcerror(Qarks.up+Qarks.charm,math.sqrt(pow(Qarks.erru,2)+pow(Qarks.errc,2)),Qarks.up+Qarks.charm+Qarks.down+Qarks.bottom+Qarks.strange,math.sqrt(pow(Qarks.erru,2)+pow(Qarks.errc,2)+pow(Qarks.errd,2)+pow(Qarks.errb,2)+pow(Qarks.errs,2)),"ratio")
		
		#Calculate combined polarisation and corresponding errors
		denom=rU*Upvals.xsec+rD*Downvals.xsec
		pol[0]=(rU*Upvals.pol*Upvals.xsec+rD*Downvals.pol*Downvals.xsec)/denom
		deriv1=(Upvals.pol*Upvals.xsec)/denom-(Upvals.pol*Upvals.xsec*rU)*(Upvals.xsec-Downvals.xsec)/pow(denom,2)
		deriv2=-(Downvals.pol*Downvals.xsec)/denom-(Downvals.pol*Downvals.xsec*rD)*(Upvals.xsec-Downvals.xsec)/pow(denom,2)
		polerr[0]=math.sqrt(pow(deriv1,2)+pow(deriv2,2))*rerr

		#Calculate combined cross-section and corresponding errors
		xsec[0]=Upvals.xsec*(Qarks.up+Qarks.charm)+Downvals.xsec*(Qarks.down+Qarks.strange+Qarks.bottom)
		xsecerr[0]=math.sqrt(pow(Upvals.xsec,2)*(pow(Qarks.erru,2)+pow(Qarks.errc,2))+pow(Downvals.xsec,2)*(pow(Qarks.errd,2)+pow(Qarks.errs,2)+pow(Qarks.errb,2)))
		
		#Fill the calculated data into the tree
		newtree.Fill()

	#Write the tree into the Datafile
	tools.write_object(Datafile,newtree,"Combined/Combined%s"%sineff[i].replace("=",""))

#Close the Datafile
Datafile.Close()

