import ROOT
import os
import math


#Function to calculate the error of a product
def producterr2(x,xerr,y,yerr):
    return math.sqrt(pow(x*yerr,2)+pow(y*xerr,2))

#Function to calculate the error of a product of 3 constituents
def producterr3(x,xerr,y,yerr,z,zerr):
    return math.sqrt(pow(y*z*xerr,2)+pow(x*z*yerr,2)+pow(x*y*zerr,2))

#Function to calculate the error of a ratio
def ratioerr(x,xerr,y,yerr):
    return math.sqrt(pow(xerr/y,2)+pow(x*yerr/pow(y,2),2))


#Open ROOT file and extracting the example count histogram
Histfile=ROOT.TFile("../data/genBosonLV_M__.root")
Nhist=Histfile.Get("ztt")


#Extracting bin information from the count histogram
NbinN=Nhist.GetNbinsX()
LowEdgeN=Nhist.GetBinLowEdge(1)
HighEdgeN=Nhist.GetBinLowEdge(NbinN+1)
StepN=(HighEdgeN-LowEdgeN)/NbinN
#print "Intervall: ", [LowEdgeN,HighEdgeeff],";", "Nbin =",NbinN,";", "step =", Stepeff

lendsin2T=0.200
rendsin2T=0.250
stepsin2T=0.005
nstepsin2T=(rendsin2T-lendsin2T)/stepsin2T
sineff=[]
for i in range(int(nstepsin2T+2)):
    sineff.append("SINEFF%s"%(lendsin2T+i*stepsin2T))

#Initialising final Graph
finalgraph=ROOT.TGraphErrors(len(sineff))
finalval=ROOT.TGraph(len(sineff))
finalerr=ROOT.TGraph(len(sineff))
workinggraph=ROOT.TGraph(len(sineff))

#Opening the datafile
Datafile=ROOT.TFile("data.root")

for l in range(len(sineff)):
    
    #Extracting Polarisation data
    ttree=Datafile.Get("Combined/Combined%s"%sineff[l])
    ttree.Draw("pol:energy>>gpol(%s,%s,%s)"%(NbinN,LowEdgeN,HighEdgeN))
    polGraph=ROOT.TGraph(ttree.GetSelectedRows(),ttree.GetV2(),ttree.GetV1())
    ttree.Draw("polerr:energy>>gpolerr(%s,%s,%s)"%(NbinN,LowEdgeN,HighEdgeN))
    polerrGraph=ROOT.TGraph(ttree.GetSelectedRows(),ttree.GetV2(),ttree.GetV1())


    #Copying count-histogram
    polNhist=ROOT.TH1D(Nhist)

    #Looping over each bin of the count-histogram
    for n in range(NbinN):

        #Initialise temporare variables
        N=polGraph.GetN()
        entemp=ROOT.Double(0.)
        poltemp=ROOT.Double(0.)


        #Initialising final variables
        energyfinal=ROOT.Double(0.)
        polfinal=ROOT.Double(0.)
        polerrfinal=ROOT.Double(0.)
        Nfinal=ROOT.Double(0.)
        Nfinalerr=ROOT.Double(0.)
        Nfinal=Nhist.GetBinContent(n+1)
#        Nfinalerr=
        energyfinal=ROOT.Double(Nhist.GetXaxis().GetBinCenter(n+1))

        #Looping over each point of the graphs
        for i in range(N):
            polGraph.GetPoint(i,entemp,poltemp)

            #If the bincenter equals the energy of a point, set the values
            if energyfinal==entemp:

                polGraph.GetPoint(i,energyfinal,polfinal)
                polerrGraph.GetPoint(i,energyfinal,polerrfinal)

                break

            #If the bincenter does not equal the energy of a point, do a linear Regression with the adjacent points and calculate the values with it
            elif energyfinal<entemp:

                polfinal=polGraph.Eval(energyfinal)
                polerrfinal=polerrGraph.Eval(energyfinal)

                break

        #Fill the calculated final values into the histograms
        polNhist.SetBinContent(n+1,polfinal*Nfinal)
        polNhist.SetBinError(n+1,producterr2(polfinal,polerrfinal,Nfinal,Nfinalerr))


    #Calculate the integral values of the histograms 
    polNinterr=ROOT.Double(0.)
    Ninterr=ROOT.Double(0.)
    polNint=polNhist.IntegralAndError(1,NbinN,polNinterr)
    Nint=Nhist.IntegralAndError(1,NbinN,Ninterr)

    #Calculate average polarisation from the integrated values
    averagepol=polNint/Nint
    averagepolerr=ratioerr(polNint,polNinterr,Nint,Ninterr)

    print "%s +/- %s" %(averagepol,averagepolerr)

    #Fill the final values into a graph
    finalgraph.SetPoint(l,lendsin2T+l*stepsin2T,averagepol)
    finalgraph.SetPointError(l,0,averagepolerr)
    finalval.SetPoint(l,lendsin2T+l*stepsin2T,averagepol)
    finalerr.SetPoint(l,lendsin2T+l*stepsin2T,averagepolerr)
    workinggraph.SetPoint(l,averagepol,lendsin2T+l*stepsin2T)


    if lendsin2T+l*stepsin2T==0.23:
        polGraph.SetTitle("Polarization of #tau's at sin^{2}(#theta_{W})=0.23")
        polGraph.GetXaxis().SetTitle("#sqrt{s}")
        polGraph.GetYaxis().SetTitle("Polarization")
        myfirstCanvas=ROOT.TCanvas()
        myfirstCanvas.cd()
        polGraph.Draw()
        myfirstCanvas.SaveAs("PolarisationGraph.pdf")
  


#Calculate the average Polarization for a given value of sin2T
sin2Tval=0.2311612
print "For a sin2T value of %s a polarization value of %s +/- %s is obtained." %(sin2Tval,finalval.Eval(sin2Tval),finalerr.Eval(sin2Tval))

#Calculate the sin2T for a given value of the average Polarization
averagePol=-0.15514
averagePolerr=0.02
print "For an average Polarization value of %s +/- %s a sin2T value of %s +/- %s is obtained" %(averagePol,averagePolerr,workinggraph.Eval(averagePol),workinggraph.Eval(averagePol+averagePolerr)-workinggraph.Eval(averagePol))


mythirdCanvas=ROOT.TCanvas()
Nhist.SetTitle("Efficiency-Histogram")
Nhist.GetXaxis().SetTitle("#sqrt{s}")
Nhist.GetYaxis().SetTitle("efficiency")
Nhist.Draw("L")
mythirdCanvas.SaveAs("Efficiency-Histogram.pdf")


"""
myfourthCanvas=ROOT.TCanvas()
effhist2.SetTitle("Efficiency-Histogram")
effhist2.GetXaxis().SetTitle("#sqrt{s}")
effhist2.GetYaxis().SetTitle("efficiency")
effhist2.Draw()
myfourthCanvas.SaveAs("Efficiency-Histogram2.pdf")
"""
myCanvas=ROOT.TCanvas()

"""
myCanvas.Divide(4,2)
myCanvas.cd(1)
polGraph.Draw()
myCanvas.cd(2)
polerrGraph.Draw()
myCanvas.cd(3)
xsecGraph.Draw()
myCanvas.cd(4)
xsecerrGraph.Draw()
myCanvas.cd(5)
effhist.Draw()
myCanvas.cd(6)
polxseceffhist.Draw()
myCanvas.cd(7)
xseceffhist.Draw()
myCanvas.cd(8)
"""
finalgraph.SetTitle("Calibration Curve")
finalgraph.GetXaxis().SetTitle("sin^{2}(#theta_{W})")
finalgraph.GetYaxis().SetTitle("#LTP_{#tau}#GT")
finalgraph.Draw()
myCanvas.SaveAs("CalibrationGraph.pdf")
#os.system("gnome-open testhist.pdf")
os.system("gnome-open CalibrationGraph.pdf")
#Histfile.Close()
