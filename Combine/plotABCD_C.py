import uproot
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
import numpy as np
import scipy.optimize as spo
import scipy.interpolate as spi

def plot(path, label):
  f = uproot.open(path)
  scan = f["limit"].arrays(["deltaNLL", "ABCD_C"])
  r = scan["ABCD_C"][1:]
  NLL = scan["deltaNLL"][1:]
  plt.plot(r, NLL, label=label)

  return r, NLL

def load(path):
  f = uproot.open(path)
  scan = f["limit"].arrays(["deltaNLL", "ABCD_C"])
  r = scan["ABCD_C"][1:]
  NLL = scan["deltaNLL"][1:]
  return r, NLL

path = sys.argv[1]

plot(path, "")
r, NLL = load(path)

spline = spi.interp1d(r, NLL)

rmin = r[np.argmin(NLL)]
rl = spo.bisect(lambda x: spline(x)-0.5, r[0], rmin)
rr = spo.bisect(lambda x: spline(x)-0.5, rmin, r[-1])
print(rl, rr)

plt.ylabel("$\Delta$ NLL")
plt.xlabel("ABCD_C")
plt.legend()
plt.ylim(bottom=0)
plt.savefig("%s.pdf"%"test")
plt.savefig("%s.png"%"test")
