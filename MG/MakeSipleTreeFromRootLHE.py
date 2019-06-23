#!/usr/bin/env python

import os
import sys
import argparse
import ROOT
import math
from array import array

from DataFormats.FWLite import Runs,Handle
from DataFormats.FWLite import Events
# run dasgoclient --query "file dataset=/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIIWinter15wmLHE-MCRUN2_71_V1_ext1-v1/LHE"emacs
# for a file list
#

source = "externalLHEProducer"

events = Events("root://cms-xrd-global.cern.ch//store/mc/RunIIWinter15wmLHE/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/LHE/MCRUN2_71_V1_ext1-v1/40000/06E42D3F-5C88-E511-A8FB-00221982AF2D.root")

hepupHandle = Handle("const lhef::HEPEUP")
eventLHEHandle = Handle("LHEEventProduct")



output_tree = ROOT.TTree()
output_tree.SetName("rootlhe")

mass = array( 'f', [ 0 ] )
spinm = array( 'f', [ 0 ] )
spinp = array( 'f', [ 0 ] )

output_tree.Branch("mass",mass , "mass/F")
output_tree.Branch("spinm",spinm , "spinm/F")
output_tree.Branch("spinp",spinp , "spinp/F")


for i,event in enumerate(events):
    event.getByLabel(source, eventLHEHandle)

    taum = ROOT.TLorentzVector(0,0,0,0)
    taup = ROOT.TLorentzVector(0,0,0,0)
    for ip, pdgid in  enumerate(eventLHEHandle.product().hepeup().IDUP):
        if pdgid==15:
            taum.SetPxPyPzE(eventLHEHandle.product().hepeup().PUP[ip][0],
                            eventLHEHandle.product().hepeup().PUP[ip][1],
                            eventLHEHandle.product().hepeup().PUP[ip][2],
                            eventLHEHandle.product().hepeup().PUP[ip][3])
            spinm[0] = eventLHEHandle.product().hepeup().SPINUP[ip]
    for ip, pdgid in  enumerate(eventLHEHandle.product().hepeup().IDUP):
        if pdgid==-15:
            taup.SetPxPyPzE(eventLHEHandle.product().hepeup().PUP[ip][0],
                            eventLHEHandle.product().hepeup().PUP[ip][1],
                            eventLHEHandle.product().hepeup().PUP[ip][2],
                            eventLHEHandle.product().hepeup().PUP[ip][3])
            spinp[0] = eventLHEHandle.product().hepeup().SPINUP[ip]
    mass[0] = (taum + taup).M()
    if mass[0] > 0:
        output_tree.Fill()
        

output_file = ROOT.TFile("SimpleTreeFromRootLHE.root", "RECREATE")
output_tree.SetDirectory(output_file)
output_file.Write()
output_file.Close()





#events = Events("root://cms-xrd-global.cern.ch//store/mc/RunIIWinter15wmLHE/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/LHE/MCRUN2_71_V1_ext1-v1/40000/C093AFAC-5D88-E511-A613-44A8423D7989.root")
#events = Events("root://cms-xrd-global.cern.ch//store/mc/RunIIWinter15wmLHE/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/LHE/MCRUN2_71_V1_ext1-v1/40000/AE505FD0-5C88-E511-96B8-20CF3027A5D4.root")
#events = Events("root://cms-xrd-global.cern.ch//store/mc/RunIIWinter15wmLHE/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/LHE/MCRUN2_71_V1_ext1-v1/40000/40C53DD2-5C88-E511-9A87-44A8423CF41F.root")
#events = Events("root://cms-xrd-global.cern.ch//store/mc/RunIIWinter15wmLHE/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/LHE/MCRUN2_71_V1_ext1-v1/40000/F83F090F-5E88-E511-9161-44A8423DE404.root")
#events = Events("root://cms-xrd-global.cern.ch//store/mc/RunIIWinter15wmLHE/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/LHE/MCRUN2_71_V1_ext1-v1/30002/9295D42D-FC88-E511-9AE2-0025904B8928.root")
#events = Events("root://cms-xrd-global.cern.ch//store/mc/RunIIWinter15wmLHE/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/LHE/MCRUN2_71_V1_ext1-v1/30001/D87BDF16-FF88-E511-BB98-002590494D4C.root")
#events = Events("root://cms-xrd-global.cern.ch//store/mc/RunIIWinter15wmLHE/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/LHE/MCRUN2_71_V1_ext1-v1/30001/00A248FF-FF88-E511-AEAE-002590494D4C.root")
#events = Events("root://cms-xrd-global.cern.ch//store/mc/RunIIWinter15wmLHE/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/LHE/MCRUN2_71_V1_ext1-v1/30001/3AB3C770-0089-E511-A810-002590494D4C.root")
#events = Events("root://cms-xrd-global.cern.ch//store/mc/RunIIWinter15wmLHE/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/LHE/MCRUN2_71_V1_ext1-v1/30001/F82BB583-0089-E511-AC1B-00259081EDD6.root")
#events = Events("root://cms-xrd-global.cern.ch//store/mc/RunIIWinter15wmLHE/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/LHE/MCRUN2_71_V1_ext1-v1/30001/BE15EDB4-158D-E511-9122-F01FAFE159CB.root")
#events = Events("root://cms-xrd-global.cern.ch//store/mc/RunIIWinter15wmLHE/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/LHE/MCRUN2_71_V1_ext1-v1/80000/2EF4EE6C-8A88-E511-866B-00259090768E.root")
#events = Events("root://cms-xrd-global.cern.ch//store/mc/RunIIWinter15wmLHE/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/LHE/MCRUN2_71_V1_ext1-v1/80000/4ED0C17F-8A88-E511-BFB6-00259090915E.root")
#events = Events("root://cms-xrd-global.cern.ch//store/mc/RunIIWinter15wmLHE/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/LHE/MCRUN2_71_V1_ext1-v1/80000/782400AA-8A88-E511-BF30-002590908462.root")
#events = Events("root://cms-xrd-global.cern.ch//store/mc/RunIIWinter15wmLHE/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/LHE/MCRUN2_71_V1_ext1-v1/80000/4EB3846B-8A88-E511-AAC8-002590907876.root")
#events = Events("root://cms-xrd-global.cern.ch//store/mc/RunIIWinter15wmLHE/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/LHE/MCRUN2_71_V1_ext1-v1/80000/D0471476-8988-E511-8C0B-00259090768E.root")
#events = Events("root://cms-xrd-global.cern.ch//store/mc/RunIIWinter15wmLHE/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/LHE/MCRUN2_71_V1_ext1-v1/80001/DE4B095A-9E88-E511-ADA8-001EC9ADDDA8.root")
#events = Events("root://cms-xrd-global.cern.ch//store/mc/RunIIWinter15wmLHE/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/LHE/MCRUN2_71_V1_ext1-v1/80001/58EA0E5A-9E88-E511-957F-001EC9ADE74E.root")
#events = Events("root://cms-xrd-global.cern.ch//store/mc/RunIIWinter15wmLHE/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/LHE/MCRUN2_71_V1_ext1-v1/80001/6C0D4759-9E88-E511-9616-0CC47A12435E.root")
#events = Events("root://cms-xrd-global.cern.ch//store/mc/RunIIWinter15wmLHE/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/LHE/MCRUN2_71_V1_ext1-v1/80001/56C07F65-9E88-E511-8285-001EC9ADDC63.root")
#events = Events("root://cms-xrd-global.cern.ch//store/mc/RunIIWinter15wmLHE/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/LHE/MCRUN2_71_V1_ext1-v1/80001/A03FE65D-9E88-E511-8DE7-0CC47A123FDC.root")
#events = Events("root://cms-xrd-global.cern.ch//store/mc/RunIIWinter15wmLHE/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/LHE/MCRUN2_71_V1_ext1-v1/80000/046DB15A-9F88-E511-A0B8-D4AE52806A65.root")
#events = Events("root://cms-xrd-global.cern.ch//store/mc/RunIIWinter15wmLHE/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/LHE/MCRUN2_71_V1_ext1-v1/80000/6A6BE4D4-A188-E511-A6E6-F01FAFE0F3DA.root")
#events = Events("root://cms-xrd-global.cern.ch//store/mc/RunIIWinter15wmLHE/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/LHE/MCRUN2_71_V1_ext1-v1/80000/56D2A921-A188-E511-96F7-F01FAFE0F3DA.root")
#events = Events("root://cms-xrd-global.cern.ch//store/mc/RunIIWinter15wmLHE/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/LHE/MCRUN2_71_V1_ext1-v1/80000/42CCA12A-A188-E511-BD4D-90B11C4434E7.root")
#events = Events("root://cms-xrd-global.cern.ch//store/mc/RunIIWinter15wmLHE/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/LHE/MCRUN2_71_V1_ext1-v1/80000/92E05337-A188-E511-93F2-003048F317C4.root")
#events = Events("root://cms-xrd-global.cern.ch//store/mc/RunIIWinter15wmLHE/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/LHE/MCRUN2_71_V1_ext1-v1/40001/1C45D00B-6288-E511-92AA-848F69FD2907.root")
#events = Events("root://cms-xrd-global.cern.ch//store/mc/RunIIWinter15wmLHE/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/LHE/MCRUN2_71_V1_ext1-v1/30000/ACBFAC3C-EE8E-E511-872E-D4AE52806A65.root")

