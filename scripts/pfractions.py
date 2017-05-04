import ROOT
import os
import math
import numpy as np

#Function from setkitanalysis which writes an object into a TFile
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


#Storing fraction values of quarks for energies in data.root
f=ROOT.TFile("../data/data.root","UPDATE")
tree=ROOT.TTree()
tree.ReadFile("../pdf/FileWithIntegrals.dat","energy:down:errd:up:erru:strange:errs:charm:errc:bottom:errb")
tree.SetName("Fractions")
write_object(f,tree,"Fractions/Fractions")
f.Write()
f.Close()
