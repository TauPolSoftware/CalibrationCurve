# Checkout

```bash
git clone --recursive https://github.com/TauPolSoftware/CalibrationCurve.git TauPolSoftware/CalibrationCurve
```

# Running

1. The **runZFitter.py** script runs ZFitter to calculate the polarisation as a function of the waek mixing angle, the Z boson mass and the quark type.
	```bash
	runZFitter.py
	```

1. The mapping between the average polarisation and the weak mixing angle is defined by the calibration curve. It depends on the event selection and must therefore be retrieved for each category separately.
	```bash
	getCalibrationCurve.py -h
	getCalibrationCurve.py -u <path/to/file.root:path/to/histogram> -d <path/to/file.root:path/to/histogram>
	```
