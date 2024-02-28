import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import glob
import numpy as np

mx = []
CLs = []
uncert = []
for f in glob.glob("*toys_CLs*"):
  finished = False

  with open(f, "r") as ff:
    res = ff.read()
  for line in res.split("\n"):
    if line[:3] == "CLs":
      mx.append(int(f.split("mx")[1].split("my")[0]))
      CLs.append(float(line.split(" ")[2]))
      uncert.append(float(line.split(" ")[-1]))
      finished=True

  if not finished:
    print("Job not finished")

mx = np.array(mx)
CLs = np.array(CLs)
uncert = np.array(uncert)

mx = mx[CLs < 0.2]
uncert = uncert[CLs < 0.2]
CLs = CLs[CLs < 0.2]

plt.xlim(min(mx)-10, max(mx)+10)
plt.axhline(y=0.05, color="red")
plt.axhline(y=0.04, color="blue")
plt.axhline(y=0.06, color="blue")
plt.errorbar(mx, CLs, uncert, fmt='ko')
plt.xlabel("mX")
plt.ylabel("CLs")
plt.savefig("CLs_comparison.png")
