import ROOT
import os
import fileinput
#import Artus.HarryPlotter.utilty.roottools as rt

#Function for filling TFiles (from setkitanalysis)
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

"""
#open ROOT File and extracting the histogram
f=ROOT.TFile("plot.root")
h=f.Get("nick0")


#Extracting bin information
Nbin=h.GetNbinsX()
a=h.GetBinLowEdge(1)
b=h.GetBinLowEdge(Nbin+1)
step=(b-a)/Nbin

#Printing the intervall, the binnumber and the stepsize
print "Intervall: ", [a,b],";", "Nbin =",Nbin,";", "step =", step

#Loop over Histogram
for n in range(0,Nbin):
    print a+n*step
"""


#Obtaining P(s) and sigma(s) from ZFitter for different sin2T and setting range and steps of energy for which the values shall be calculated

#left end, right end, stepsize and number of steps for sin2T; create an array for sin2T for the values
lendsin2T=0.200
rendsin2T=0.250
stepsin2T=0.005
nstepsin2T=(rendsin2T-lendsin2T)/stepsin2T
sineff=[]
for i in range(int(nstepsin2T+2)):
    sineff.append("SINEFF=%s"%(lendsin2T+i*stepsin2T))


#left end, right end, stepsize and number of steps for s (energy)
lends=80.
rends=110.
steps=0.25
nsteps=(rends-lends)/steps+1


#starting the process for U and D quarks
for n in range(2):

    #Copying files to substitute to ZFitter folder
    os.system("cp ../zFitter/FilesToSubstitute/dizet6_42.f ../zFitter/dizet6_42.f")
    if n==0:
        os.system("cp ../zFitter/FilesToSubstitute/zfusr6_42d.f ../zFitter/zfusr6_42.f")
    else:
        os.system("cp ../zFitter/FilesToSubstitute/zfusr6_42u.f ../zFitter/zfusr6_42.f")

    #writing range of energy and steps into file
    for line in fileinput.input("../zFitter/zfusr6_42.f",inplace=True):
        print line.rstrip().replace("DO I = 1,560","DO I = 1,%s"%nsteps)
    for line in fileinput.input("../zFitter/zfusr6_42.f",inplace=True):
        print line.rstrip().replace("RS = 35.0+0.25*(I-1)","RS = %s+%s*(I-1)"%(lends,steps))



    #looping over all requested values for sin2T
    for i in range(len(sineff)):
        print "%s. run: compiling ZFitter, running ZFitter"%i
        
        #setting names for output
        if n==0:
            if i==0:
                for line in fileinput.input("../zFitter/zfusr6_42.f",inplace=True):
                    print line.rstrip().replace("PolarizationAndXsecQuarkD_UNDEFINED","PolarizationAndXsecQuarkD_%s"%sineff[i])
            else: 
                for line in fileinput.input("../zFitter/zfusr6_42.f",inplace=True):
                    print line.rstrip().replace("PolarizationAndXsecQuarkD_%s"%sineff[i-1],"PolarizationAndXsecQuarkD_%s"%sineff[i])

        else:
            if i==0:
                for line in fileinput.input("../zFitter/zfusr6_42.f",inplace=True):
                    print line.rstrip().replace("PolarizationAndXsecQuarkU_UNDEFINED","PolarizationAndXsecQuarkU_%s"%sineff[i])
            else:
                for line in fileinput.input("../zFitter/zfusr6_42.f",inplace=True):
                    print line.rstrip().replace("PolarizationAndXsecQuarkU_%s"%sineff[i-1],"PolarizationAndXsecQuarkU_%s"%sineff[i])

        #setting sin2T value
        if i==0:
            for line in fileinput.input("../zFitter/dizet6_42.f",inplace=True):
                print line.rstrip().replace("SINEFF=UNDEFINED",sineff[0])
            print "(SINEFF=UNDEFINED to %s)"%sineff[0]
        else:
            for line in fileinput.input("../zFitter/dizet6_42.f",inplace=True):
                print line.rstrip().replace(sineff[i-1],sineff[i])
            print "(%s to %s)"%(sineff[i-1],sineff[i])

        #compile ZFitter
        os.system("cd ../zFitter && g77 -g  -fno-automatic -fdollar-ok -fno-backslash -finit-local-zero -fno-second-underscore -fugly-logint -ftypeless-boz  *.f -o zfitr642.exe")

        #starting ZFitter
        os.system("../zFitter/zfitr642.exe")


#Writing data into TFile
Datfile=ROOT.TFile("../data/data.root","RECREATE")

for n in range(2):
    for i in range(len(sineff)):
        tree=ROOT.TTree()
        if n==0:
            tree.ReadFile("PolarizationAndXsecQuarkD_%s.dat"%sineff[i],"s:xsec:pol")
            tree.SetName("Down %s"%sineff[i])
            write_object(Datfile,tree,"Down/Down%s"%sineff[i].replace("=",""))
            Datfile.Write()
        else:
            tree.ReadFile("PolarizationAndXsecQuarkU_%s.dat"%sineff[i],"s:xsec:pol")
            tree.SetName("Up %s"%sineff[i])
            write_object(Datfile,tree,"Up/Up%s"%sineff[i].replace("=",""))
            Datfile.Write()
Datfile.Close()

#Deleting .dat files after they were written into the TFile
#os.system("/.automount/home/home__home2/institut_3b/vannahme/PolarizationCalibrationCurve/")
for i in range(len(sineff)):
    os.system("rm PolarizationAndXsecQuarkU_%s.dat"%sineff[i])
    os.system("rm PolarizationAndXsecQuarkD_%s.dat"%sineff[i])

