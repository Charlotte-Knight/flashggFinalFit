import ROOT

import numpy as np
import scipy.interpolate as spi
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import argparse
import json
import os

DO_SYST = False

def loadJson(path):
  with open(path, "r") as f:
    return json.load(f)

def unique(a, b):
  return 0.5*(a+b)*(a+b+1)+b

def makeWorkspace(indir, year, cat, workspace_output):
  suffix = "_%s_cat%s"%(year, cat)

  model_path = os.path.join(indir, year, cat, "model.json")
  model = loadJson(model_path)
  mx = model.keys()
  mx = np.sort(np.array(mx, dtype=float))
  
  norms = np.asarray([model[str(m)][0] for m in mx])
  popts = np.asarray([model[str(m)][1] for m in mx])
  mx = np.asarray(mx)

  MX = ROOT.RooRealVar("MX", "MY", mx.min(), mx.min(), mx.max())
  sig_norm_nominal = ROOT.RooSpline1D("sig_norm_nominal"+suffix, "sig_norm_nominal"+suffix, MX, len(mx), mx, norms)

  CMS_hgg_mass = ROOT.RooRealVar("CMS_hgg_mass", "CMS_hgg_mass", 100, 65, 180)
  dZ = ROOT.RooRealVar("dZ", "dZ", 0, -20, 20)
  MH = ROOT.RooRealVar("MH", "MH", 100, 65, 180)
  
  mean_nominal = ROOT.RooSpline1D("mean_nominal"+suffix, "mean_nominal"+suffix, MX, len(mx), mx, np.array(popts[:, 1]))
  sigma_nominal = ROOT.RooSpline1D("sigma_nominal"+suffix, "sigma_nominal"+suffix, MX, len(mx), mx, np.array(popts[:, 2]))
  n1 = ROOT.RooSpline1D("n1"+suffix, "n1"+suffix, MX, len(mx), mx, np.array(popts[:, 4]))
  n2 = ROOT.RooSpline1D("n2"+suffix, "n2"+suffix, MX, len(mx), mx, np.array(popts[:, 6]))
  a1 = ROOT.RooSpline1D("a1"+suffix, "a1"+suffix, MX, len(mx), mx, np.array(popts[:, 3]))
  a2 = ROOT.RooSpline1D("a2"+suffix, "a2"+suffix, MX, len(mx), mx, np.array(popts[:, 5]))

  if DO_SYST:
    systematics_path = os.path.join(args.indir, year, cat, "systematics.json")
    systematics = loadJson(systematics_path)

    #creates splines for const values
    const_sys_names = [name for name in systematics[str(mx[0])].keys() if "const" in name]
    consts_splines = {}
    for systematic in const_sys_names:
      values = np.asarray([systematics[str(m)][systematic] for m in mx])
      consts_splines[systematic] = ROOT.RooSpline1D(systematic+suffix, systematic+suffix, MX, len(mx), mx, values)

    #create nuisances
    nuisances = {}
    nuisance_names = set([name.split("_")[2] for name in const_sys_names])
    for name in nuisance_names:
      nuisances[name] = ROOT.RooRealVar("nuisance_%s"%name, "nuisance_%s"%name, 0, -5, 5)

    #create RooFormulaVars including the systematics
    get_nuisance = lambda name, var: nuisances[name]
    get_const = lambda name, var: consts_splines["const_%s_%s"%(var, name)]

    formula = "@0*(1." + "".join(["+@%d*@%d"%(i*2+1,i*2+2) for i in range(len(const_sys_names)//3)]) + ")"
    print(formula)
    print(sig_norm_nominal)
    
    sig_norm = ROOT.RooFormulaVar("sig%s_norm"%suffix, "sig%s_norm"%suffix, formula, ROOT.RooArgList(sig_norm_nominal, *[f(name, "rate") for name in nuisance_names for f in (get_const, get_nuisance)]))
    mean = ROOT.RooFormulaVar("mean"+suffix, "mean"+suffix, formula,  ROOT.RooArgList(mean_nominal, *[f(name, "mean") for name in nuisance_names for f in (get_const, get_nuisance)]))
    sigma = ROOT.RooFormulaVar("sigma"+suffix, "sigma"+suffix, formula,  ROOT.RooArgList(sigma_nominal, *[f(name, "sigma") for name in nuisance_names for f in (get_const, get_nuisance)]))
  else:
    sig_norm = ROOT.RooFormulaVar("sig%s_norm"%suffix, "sig%s_norm"%suffix, "@0", ROOT.RooArgList(sig_norm_nominal))
    mean = ROOT.RooFormulaVar("mean"+suffix, "mean"+suffix, "@0", ROOT.RooArgList(mean_nominal))
    sigma = ROOT.RooFormulaVar("sigma"+suffix, "sigma"+suffix, "@0", ROOT.RooArgList(sigma_nominal))
  
  sig = ROOT.RooDoubleCBFast("sig"+suffix, "sig"+suffix, CMS_hgg_mass, mean, sigma, a1, n1, a2, n2)

  wsig_13TeV = ROOT.RooWorkspace("wsig_13TeV", "wsig_13TeV")

  imp = getattr(wsig_13TeV, "import")

  imp(CMS_hgg_mass)
  imp(MH)
  imp(dZ)

  imp(sig_norm)
  imp(sig)

  #wsig_13TeV.Print()
  wsig_13TeV.writeToFile(workspace_output)

def tryMake(path):
  if not os.path.exists(path):
    os.makedirs(path)

def main(args):
  years = filter(lambda x: os.path.isdir(os.path.join(args.indir, x)), os.listdir(args.indir))
  cats = filter(lambda x: os.path.isdir(os.path.join(args.indir, years[0], x)), os.listdir(os.path.join(args.indir, years[0])))
  #print(years)
  #print(cats)
  tryMake(args.outdir)

  for year in years:
    for cat in cats:
      out_path = os.path.join(args.outdir, "sig_%s_cat%s.root"%(year, cat))
      makeWorkspace(args.indir, year, cat, out_path)

if __name__=="__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--indir', '-i', type=str, required=True)
  parser.add_argument('--outdir', '-o', type=str, required=True)
  args = parser.parse_args()

  main(args)


