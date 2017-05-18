import pylab as py
import matplotlib.colors
import json

from measurements.libs import SPE3read as spe3

fName = 'D:/2017 May 16 16_55_44.spe'
data = spe3.SPE3map(fName)

wavelength = data.wavelength
wavelengthRangeMeas = (wavelength[0], wavelength[-1])
nbOfFrames = data.nbOfFrames
counts = py.array([dataRow[0] for dataRow in data.data])
exposureTime = data.exposureTime  # exposure time in ms

print wavelength
print counts




py.plot (wavelength, counts[1,:])
plt.show()