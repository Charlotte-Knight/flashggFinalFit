import uproot
import os
import numpy as np
import scipy.stats as sps

def getPval(sig):
  return 2 * (1-sps.norm.cdf(sig))
getPvalVec = np.vectorize(getPval)

files = os.listdir(".")
files = list(filter(lambda x: "Significance" in x, files))

files = [list(filter(lambda x: "left" in x, files)), list(filter(lambda x: "right" in x, files))]

r = []
sig = []
for i, file_set in enumerate(files):
  r.append([])
  sig.append([])
  for j, f in enumerate(file_set):
    r[i].append(float(".".join(f.split("_")[2].split(".")[:2])))
    with uproot.open(f) as fup:
      sig[i].append(fup["limit/limit"].array()[0])

r = np.array(r)
sig = np.array(sig)

s = np.argsort(r[0])
r[0] = r[0][s]
sig[0] = sig[0][s]

s = np.argsort(r[1])
r[1] = r[1][s]
sig[1] = sig[1][s]

pval = getPvalVec(sig)

for i in range(len(r[0])):
  print("%.2f"%r[0][i], "%.2f"%r[1][i], "%.2f"%sig[0][i], "%.2f"%sig[1][i], "%.3f"%(sig[0][i]/sig[1][i]), "%.3f"%pval[0][i], "%.3f"%pval[1][i], "%.2f"%(pval[0][i]/pval[1][i]))


