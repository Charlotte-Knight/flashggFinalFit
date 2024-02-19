import sys
import os
import matplotlib.pyplot as plt

left_files = list(filter(lambda x: "veto" in x, os.listdir(sys.argv[1])))
right_files = list(filter(lambda x: "veto" in x, os.listdir(sys.argv[2])))

left_mx = [int(f.split("mx")[1].split("my")[0]) for f in left_files]
right_mx = [int(f.split("mx")[1].split("my")[0]) for f in right_files]

left_eff = []
left_eff_err = []
for f in left_files:
  with open(os.path.join(sys.argv[1],f), "r") as f:
    text = f.read()[1:-2]
    print(text.split(", ")[0].strip())
    left_eff.append(float(text.split(", ")[0].strip()))
    left_eff_err.append(float(text.split(", ")[1].strip()))

right_eff = []
right_eff_err = []
for f in right_files:
  with open(os.path.join(sys.argv[2],f), "r") as f:
    text = f.read()[1:-2]
    print(text)
    right_eff.append(float(text.split(", ")[0].strip()))
    right_eff_err.append(float(text.split(", ")[1].strip()))

plt.errorbar(left_mx, left_eff, left_eff_err, label="Left", fmt=".")
plt.errorbar(right_mx, right_eff, right_eff_err, label="Right", fmt=".")
plt.legend()
plt.ylabel("Veto Efficiency")
plt.xlabel(r"$m_X$")
plt.xlim(250, 1050)
plt.savefig("veto_eff.png")
    
