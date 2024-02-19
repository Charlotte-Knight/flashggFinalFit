import ROOT
import sys
import numpy as np
import uproot
import scipy.optimize as spo
import scipy.interpolate as spi
import matplotlib.pyplot as plt

def processScan(path, var):
  f = uproot.open(path.replace("VAR", var))
  scan = f["limit"].arrays(["deltaNLL", var])
  r = scan[var][1:]
  NLL = scan["deltaNLL"][1:]

  spline = spi.interp1d(r, NLL)
  rmin = r[np.argmin(NLL)]
  
  rr = spo.bisect(lambda x: spline(x)-0.5, rmin, r[-1])

  if spline(r[0]) < 0.5:
    rl = 0
  else:
    rl = spo.bisect(lambda x: spline(x)-0.5, r[0], rmin)
    
  error = max([rl, rr])

  plt.plot(r, NLL)
  plt.axvline(rl)
  plt.axvline(rmin)
  plt.axvline(rr)
  plt.savefig(path.replace("VAR", var)+".png")
  plt.clf()

  return rmin, rmin-rl, rr-rmin

# workspace_vars = []
# varIter = w.allVars().createIterator()
# var = varIter.Next()
# while var:
#   workspace_vars.append(var.GetName())
#   var = varIter.Next()

# for var in workspace_vars:
#   if ("n_exp" in var) and ("cat7_proc_dy_merged_hgg") in var:
#     ABCD_C_var = var
#   elif ("n_exp" in var) and ("cat7cr_proc_dy_merged_hgg") in var:
#     ABCD_A_var = var

ABCD_C, ABCD_C_err_l, ABCD_C_err_r = processScan(sys.argv[1], "ABCD_C")
ABCD_A, ABCD_A_err_l, ABCD_A_err_r = processScan(sys.argv[1], "ABCD_A")
#ABCD_C, ABCD_C_err_l, ABCD_C_err_r = processScan(sys.argv[1], ABCD_C_var)
#ABCD_A, ABCD_A_err_l, ABCD_A_err_r = processScan(sys.argv[1], ABCD_A_var)
ABCD_A_err = (ABCD_A_err_r-ABCD_A_err_l) / 2

eff = ABCD_C / ABCD_A
eff_err_l = eff * np.sqrt( (ABCD_C_err_l/ABCD_C)**2 + (ABCD_A_err/ABCD_A)**2 )
eff_err_r = eff * np.sqrt( (ABCD_C_err_r/ABCD_C)**2 + (ABCD_A_err/ABCD_A)**2 )
print(eff, eff_err_l, eff_err_r)
