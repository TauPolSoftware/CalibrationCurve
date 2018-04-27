#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ROOT
import os
import math
import numpy as np

import TauPolSoftware.CalibrationCurve.tools as tools


#Storing fraction values of quarks for energies in data.root
f=ROOT.TFile("../data/data.root","UPDATE")
tree=ROOT.TTree()
tree.ReadFile("../pdf/FileWithIntegrals.dat","energy:down:errd:up:erru:strange:errs:charm:errc:bottom:errb")
tree.SetName("Fractions")
tools.write_object(f,tree,"Fractions/Fractions")
f.Write()
f.Close()
