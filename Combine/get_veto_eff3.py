import ROOT
import sys
import numpy as np
import uproot
import scipy.optimize as spo
import scipy.interpolate as spi
import matplotlib.pyplot as plt

def processScan(path):
  f=uproot.open(path)
  scan = f["limit"].arrays(["deltaNLL", "veto_eff"])
  r = scan["veto_eff"][1:]
  NLL = scan["deltaNLL"][1:]

  plt.plot(r, NLL)
  plt.savefig(path+".png")
  
  spline = spi.interp1d(r, NLL)
  rmin = r[np.argmin(NLL)]
  
  rr = spo.bisect(lambda x: spline(x)-0.5, rmin, r[-1])

  if spline(r[0]) < 0.5:
    rl = 0
  else:
    rl = spo.bisect(lambda x: spline(x)-0.5, r[0], rmin)
    
  error = max([rl, rr])

  plt.axvline(rl)
  plt.axvline(rmin)
  plt.axvline(rr)
  plt.savefig(path+".png")
  plt.clf()

  return rmin, rmin-rl, rr-rmin

eff, eff_err_l, eff_err_r = processScan(sys.argv[1])
print(eff, eff_err_l, eff_err_r)
