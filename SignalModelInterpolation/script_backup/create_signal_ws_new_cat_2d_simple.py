import ROOT

import numpy as np
import scipy.interpolate as spi
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import argparse
import json
import os

def loadJson(path):
  with open(path, "r") as f:
    return json.load(f)

def unique(a, b):
  return 0.5*(a+b)*(a+b+1)+b

def makeWorkspace(models, year, cat, workspace_output, mgg_range):
  suffix = "_%s_cat%s_res_bkg"%(year, cat)

  model = models[year][cat]
  masses = model.keys()

  mx = np.array([int(m.split("_")[0]) for m in masses])
  my = np.array([int(m.split("_")[1]) for m in masses])
  mx_my = unique(mx, my)

  masses = list(np.array(masses)[np.argsort(mx_my)])
  mx_my = np.sort(mx_my)
    
  norms = np.asarray([model[m]["norm"] for m in masses])
  popts = np.asarray([model[m]["parameters"] for m in masses])
  mx_my_arr = np.asarray(mx_my, dtype=float)

  MX = ROOT.RooRealVar("MX", "MX", mx[0], mx.min(), mx.max())
  MY = ROOT.RooRealVar("MY", "MY", my[0], my.min(), my.max())
  MX_MY = ROOT.RooFormulaVar("MX_MY", "MX_MY", "0.5*(@0+@1)*(@0+@1+1)+@1", ROOT.RooArgList(MX, MY))
  
  CMS_hgg_mass = ROOT.RooRealVar("CMS_hgg_mass", "CMS_hgg_mass", mgg_range[0], mgg_range[0], mgg_range[1])
  dZ = ROOT.RooRealVar("dZ", "dZ", 0, -20, 20)
  MH = ROOT.RooRealVar("MH", "MH", mgg_range[0], mgg_range[0], mgg_range[1])

  sig_norm = ROOT.RooSpline1D("sig%s_norm"%suffix, "sig_norm"+suffix, MX_MY, len(mx_my_arr), mx_my_arr, norms)
  dm = ROOT.RooSpline1D("dm"+suffix, "dm"+suffix, MX_MY, len(mx_my_arr), mx_my_arr, np.array(popts[:, 1]))
  sigma = ROOT.RooSpline1D("sigma"+suffix, "sigma"+suffix, MX_MY, len(mx_my_arr), mx_my_arr, np.array(popts[:, 2]))

  n1 = ROOT.RooSpline1D("n1"+suffix, "n1"+suffix, MX_MY, len(mx_my_arr), mx_my_arr, np.array(popts[:, 4]))
  n2 = ROOT.RooSpline1D("n2"+suffix, "n2"+suffix, MX_MY, len(mx_my_arr), mx_my_arr, np.array(popts[:, 6]))
  a1 = ROOT.RooSpline1D("a1"+suffix, "a1"+suffix, MX_MY, len(mx_my_arr), mx_my_arr, np.array(popts[:, 3]))
  a2 = ROOT.RooSpline1D("a2"+suffix, "a2"+suffix, MX_MY, len(mx_my_arr), mx_my_arr, np.array(popts[:, 5]))

  mean = ROOT.RooFormulaVar("mean"+suffix, "mean"+suffix, "125.38+@0", ROOT.RooArgList(dm)) #fixed at 125.38 + shift
  sig = ROOT.RooDoubleCBFast("sig"+suffix, "sig"+suffix, CMS_hgg_mass, mean, sigma, a1, n1, a2, n2)

  wsig_13TeV = ROOT.RooWorkspace("wsig_13TeV", "wsig_13TeV")

  imp = getattr(wsig_13TeV, "import")

  imp(CMS_hgg_mass)
  imp(MH)
  imp(dZ)

  imp(sig)
  imp(sig_norm, ROOT.RooFit.RecycleConflictNodes())

  wsig_13TeV.var("MY").setVal(100)
  wsig_13TeV.var("MH").setVal(90)

  #wsig_13TeV.Print()
  wsig_13TeV.writeToFile(workspace_output)

def tryMake(path):
  if not os.path.exists(path):
    os.makedirs(path)

def main(args):
  with open(os.path.join(args.indir, "model.json"), "r") as f:
    models = json.load(f)
 
  years = sorted(models.keys())
  #years = ["2016"]
  cats = sorted(models[years[0]].keys())
  print(years)
  print(cats)
  tryMake(args.outdir)

  for year in years:
    for cat in cats:
      out_path = os.path.join(args.outdir, "sig_%s_cat%s.root"%(year, cat))
      makeWorkspace(models, year, cat, out_path, args.mgg_range)

if __name__=="__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--indir', '-i', type=str, required=True)
  parser.add_argument('--outdir', '-o', type=str, required=True)
  parser.add_argument('--mgg-range', type=float, nargs=2, default=(100,180))
  args = parser.parse_args()

  main(args)


