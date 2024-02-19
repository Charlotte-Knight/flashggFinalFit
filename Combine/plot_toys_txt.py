import sys

mgg = []
w = []

with open(sys.argv[1], "r") as f:
  s = f.read()
  s = s.replace(" ", "")
  lines = s.split("\n")
  for line in lines:
    if "mass" in line:
      mgg.append(float(line.split("=")[1]))
    elif ("Roo" not in line) and (line != ""):
      print(line)
      w.append(float(line))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.scatter(mgg, w)
plt.savefig("toys.png")
