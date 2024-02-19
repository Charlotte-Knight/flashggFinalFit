import ROOT
import sys

f = ROOT.TFile(sys.argv[1], "read")
dataset = f.Get("toys/toy_asimov")

for i in range(320):
  dataset.get(i).Print("CMS_hgg_mass")
  print(dataset.weight())
