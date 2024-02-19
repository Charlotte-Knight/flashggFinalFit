import ROOT
import sys
import numpy as np

f=ROOT.TFile(sys.argv[1])
w=f.Get("w")
w.loadSnapshot("MultiDimFit")

ABCD_C = w.var("ABCD_C").getVal()
ABCD_C_err = w.var("ABCD_C").getError()

ABCD_A = w.var("ABCD_A").getVal()
ABCD_A_err = w.var("ABCD_A").getError() 

eff = ABCD_C / ABCD_A
eff_err = eff * np.sqrt( (ABCD_C_err/ABCD_C)**2 + (ABCD_A_err/ABCD_A)**2 )
print(eff, eff_err)
