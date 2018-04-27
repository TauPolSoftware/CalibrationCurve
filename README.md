# PolarisationCalibrationCurve

Zfitter program is used to calculate the tau polarisation and cross section for a given energy and an effective sin2theta values 
by taking into account a different coupling of the up-type and down-type quarks.

#1.# The **runZFitter.py** script creates a root file which includes the up type and down type cross section, polarisation for various energy 
values and sin2theta determined in the script. It can be simple run by
```
python runZFitter.py
```

#2.# The next step is to take into account the fractions between up-type and down-type quarks. This is done with the **pfractions.py** script.
```
python 	pfractions.py
```

#3.# Then, the combined values of the up-type and down-type values are calculated by considering the fractions using **calcmixedpolandxsec.py**
script.
```
python 	calcmixedpolandxsec.py
```

#4.# Now, one can calculate the tau polarisations for each sin2theta as a function of energy and produce the graphs by
```
python calccalibrationcurve<2>.py   
```
