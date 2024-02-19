import sys
import os
import matplotlib.pyplot as plt

freeze = True

left_files = list(filter(lambda x: ("veto" in x) and (freeze == ("freeze" in x)), os.listdir(sys.argv[1])))
right_files = list(filter(lambda x: ("veto" in x) and (freeze == ("freeze" in x)), os.listdir(sys.argv[2])))

left_mx = [int(f.split("mx")[1].split("my")[0]) for f in left_files]
right_mx = [int(f.split("mx")[1].split("my")[0]) for f in right_files]

left_eff = []
left_eff_err_l = []
left_eff_err_r = []
for f in left_files:
  with open(os.path.join(sys.argv[1],f), "r") as f:
    text = f.read()[1:-2]
    if text == "":
      left_eff.append(0)
      left_eff_err_l.append(0)
      left_eff_err_r.append(0)
    else:
      left_eff.append(float(text.split(", ")[0].strip()))
      left_eff_err_l.append(float(text.split(", ")[1].strip()))
      left_eff_err_r.append(float(text.split(", ")[2].strip()))

right_eff = []
right_eff_err_l = []
right_eff_err_r = []
for f in right_files:
  with open(os.path.join(sys.argv[2],f), "r") as f:
    text = f.read()[1:-2]
    if text == "":
      right_eff.append(0)
      right_eff_err_l.append(0)
      right_eff_err_r.append(0)
    else:
      right_eff.append(float(text.split(", ")[0].strip()))
      right_eff_err_l.append(float(text.split(", ")[1].strip()))
      right_eff_err_r.append(float(text.split(", ")[2].strip()))

plt.errorbar(left_mx, left_eff, [left_eff_err_l, left_eff_err_r], label="Left", fmt=".")
plt.errorbar(right_mx, right_eff, [right_eff_err_l, right_eff_err_r], label="Right", fmt=".")

if len(sys.argv) > 3:
  inc_files = list(filter(lambda x: ("veto" in x) and (freeze == ("freeze" in x)), os.listdir(sys.argv[3])))

  inc_mx = [int(f.split("mx")[1].split("my")[0]) for f in inc_files]

  inc_eff = []
  inc_eff_err_l = []
  inc_eff_err_r = []
  for f in inc_files:
    with open(os.path.join(sys.argv[3],f), "r") as f:
      text = f.read()[1:-2]
      if text == "":
        inc_eff.append(0)
        inc_eff_err_l.append(0)
        inc_eff_err_r.append(0)
      else:
        inc_eff.append(float(text.split(", ")[0].strip()))
        inc_eff_err_l.append(float(text.split(", ")[1].strip()))
        inc_eff_err_r.append(float(text.split(", ")[2].strip()))

  print(inc_mx)
  print(inc_eff)
  plt.errorbar(inc_mx, inc_eff, [inc_eff_err_l, inc_eff_err_r], label="Inclusive", fmt=".")

plt.legend()
plt.ylabel("Veto Efficiency")
plt.xlabel(r"$m_X$")
plt.xlim(250, 1050)
plt.savefig("veto_eff.png")
    
