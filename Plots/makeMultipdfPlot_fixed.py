import os, sys
import re
from optparse import OptionParser
import ROOT
import pandas as pd
import numpy as np
import glob
import pickle
import math
import json
from collections import OrderedDict as od
import scipy.stats

from commonTools import *
from commonObjects import *

def get_options():
  parser = OptionParser()
  parser.add_option("--inputWSFile", dest="inputWSFile", default=None, help="Input multipdf RooWorkspace file")
  parser.add_option("--cat", dest="cat", default="RECO_0J_PTH_0_10_Tag0", help="Analysis category")
  parser.add_option("--unblind", dest="unblind", default=False, action="store_true", help="Unblind signal region")
  parser.add_option("--blindingRegion", dest="blindingRegion", default="116,134", help="Region in xvar to blind")
  parser.add_option("--doZeroes", dest="doZeroes", default=False, action="store_true", help="Add error of unity to zero bins to show on plot")
  parser.add_option("--ext", dest="ext", default='', help="Extension for saving")
  parser.add_option("--xvar", dest="xvar", default="CMS_hgg_mass,m_{#gamma#gamma},GeV", help="X-variable: name,title,units")
  parser.add_option("--nBins", dest="nBins", default=80, type='int', help="Number of bins")
  parser.add_option("--pdfNBins", dest="pdfNBins", default=3200, type='int', help="Number of bins")
  parser.add_option("--translateCats", dest="translateCats", default=None, help="JSON to store cat translations")
  parser.add_option("--do-NMSSM", dest="do_NMSSM", default=False, action="store_true", help="Process X->YH style workspace")
  parser.add_option("--do-YToGG", dest="do_YToGG", default=False, action="store_true", help="Process X->Y(gg)H")
  parser.add_option("--do-HighMass", dest="do_HighMass", default=False, action="store_true", help="Do High mass plots: log")
  
  return parser.parse_args()
(opt,args) = get_options()


print " --> Opening workspace: %s"%opt.inputWSFile
f = ROOT.TFile(opt.inputWSFile)
w = f.Get("multipdf")

w.var("CMS_hgg_mass").Print()

# Define blinding region
blindingRegion = [float(opt.blindingRegion.split(",")[0]),float(opt.blindingRegion.split(",")[1])]

# Define xvariable and categories
xvar = w.var(opt.xvar.split(",")[0])
weight = ROOT.RooRealVar("weight","weight",0)
xvar.SetTitle(opt.xvar.split(",")[1])
xvar.setPlotLabel(opt.xvar.split(",")[1])
xvar.setUnit(opt.xvar.split(",")[2])
xvar_arglist, xvar_argset = ROOT.RooArgList(xvar), ROOT.RooArgSet(xvar)
chan = w.cat("CMS_channel")


# Exact multipdf object and pdfindex
multipdf = w.pdf("CMS_hgg_%s_combined_13TeV_bkgshape"%opt.cat)
pdfindex_bf = w.cat("pdfindex_%s_combined_13TeV"%opt.cat).getIndex()
bpdf_bf_name = None
bpdfs = od()
for ipdf in range(multipdf.getNumPdfs()): 
  bpdfs[multipdf.getPdf(ipdf).GetName()] = w.pdf(multipdf.getPdf(ipdf).GetName())
  if ipdf == pdfindex_bf: bpdf_bf_name = multipdf.getPdf(ipdf).GetName()

# Make histograms from bpdfs and scale by norm
norm = w.var("CMS_hgg_%s_combined_13TeV_bkgshape_norm"%opt.cat).getVal()

hists = od()
for bname, bpdf in bpdfs.iteritems():
  hists[bname] = bpdf.createHistogram("h_%s"%bname,xvar,ROOT.RooFit.Binning(opt.pdfNBins,xvar.getMin(),xvar.getMax()))
  #hists[bname].Scale(norm)
  hists[bname].Scale(norm*(float(opt.pdfNBins)/float(opt.nBins)))

  if bname == bpdf_bf_name:
    hists["%s_nBins"%bname] = bpdf.createHistogram("h_%s_nBins"%bname,xvar,ROOT.RooFit.Binning(opt.nBins,xvar.getMin(),xvar.getMax()))
    hists["%s_nBins"%bname].Scale(norm)

# Scale pdf histograms to match data
#xvar_range = int(xvar.getBinning().highBound()-xvar.getBinning().lowBound())
#if opt.nBins != xvar_range:
#  for h in hists.itervalues(): h.Scale(float(xvar_range)/opt.nBins)

# Extract dataset and convert to histogram
# data = ROOT.RooDataSet("d","d", xvar_argset)
# d = w.data("roohist_data_mass_%s"%opt.cat)
# for i in range(d.numEntries()):
#   p = d.get(i)
#   p.Print()
#   nent = int(d.weight())
#   for ient in range(nent): data.add(p)

hists['data'] = xvar.createHistogram("h_data", ROOT.RooFit.Binning(opt.nBins,xvar.getMin(),xvar.getMax()))
hists['data'].SetBinErrorOption(ROOT.TH1.kPoisson)

data = w.data("roohist_data_mass_%s"%opt.cat)

if opt.unblind: data.fillHistogram(hists['data'],xvar_arglist)
else: data.reduce("%s<%f|%s>%f"%(xvar.GetName(),blindingRegion[0],xvar.GetName(),blindingRegion[1])).fillHistogram(hists['data'],xvar_arglist)
if opt.doZeroes:
  for ibin in range(1,hists['data'].GetNbinsX()+1):
    bcenter = hists['data'].GetBinCenter(ibin)
    # Skip blinded region
    if( not opt.unblind )&(bcenter > blindingRegion[0])&(bcenter < blindingRegion[1]): continue
    if hists['data'].GetBinContent(ibin)==0.:
      hists['data'].SetBinError(ibin,1)

# Change to poisson intervals for data histogram
for ibin in range(1,hists['data'].GetNbinsX()+1):
  bcenter = hists['data'].GetBinCenter(ibin)
  if( not opt.unblind )&(bcenter > blindingRegion[0])&(bcenter < blindingRegion[1]): continue
  bval = hists['data'].GetBinContent(ibin)
  l = scipy.stats.gamma.interval(0.68,bval)[0]
  # Catch for zero entries
  if l!=l: l = 0
  u = scipy.stats.gamma.interval(0.68,bval+1)[1]
  err = max( abs(bval-l), abs(bval-u) )
  hists['data'].SetBinError(ibin,err)

# Create ratio histograms
hists_ratio = od()
for bname in bpdfs:
  hists_ratio[bname] = hists[bname]-hists[bpdf_bf_name]

hists_ratio['data'] = hists['data'].Clone()
hists_ratio['data'].Reset()
for ibin in range(1,hists['data'].GetNbinsX()+1):
  bcenter = hists['data'].GetBinCenter(ibin)
  if(not opt.unblind)&(bcenter>blindingRegion[0])&(bcenter<blindingRegion[1]): continue
  bval, berr = hists['data'].GetBinContent(ibin), hists['data'].GetBinError(ibin)
  bkgval = hists["%s_nBins"%bpdf_bf_name].GetBinContent(ibin)
  hists_ratio['data'].SetBinContent(ibin,bval-bkgval)
  hists_ratio['data'].SetBinError(ibin,berr)

doSignal = False

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Plotting
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(True)

cat = opt.cat

def Translate(name, ndict):
    return ndict[name] if name in ndict else name
def LoadTranslations(jsonfilename):
    with open(jsonfilename) as jsonfile:
        return json.load(jsonfile)
translateCats = {} if opt.translateCats is None else LoadTranslations(opt.translateCats)


canv = ROOT.TCanvas("canv_%s"%cat,"canv_%s"%cat,1000,800)
pad1 = ROOT.TPad("pad1_%s"%cat,"pad1_%s"%cat,0,0.25,1,1)
pad1.SetTickx()
pad1.SetTicky()
pad1.SetBottomMargin(0.18)
pad1.SetLeftMargin(0.12)
pad1.Draw()
pad2 = ROOT.TPad("pad2_%s"%cat,"pad2_%s"%cat,0,0,1,0.35)
pad2.SetTickx()
pad2.SetTicky()
pad2.SetTopMargin(0.03)
pad2.SetBottomMargin(0.25)
pad2.SetLeftMargin(0.12)
pad2.Draw()
padSizeRatio = 0.65/0.45

# Axis options 
ROOT.TGaxis.SetMaxDigits(4)
ROOT.TGaxis.SetExponentOffset(-0.05,0.00,"y")

# Nominal plot
pad1.cd()
h_axes = hists['data'].Clone()
h_axes.Reset()
if opt.do_HighMass:
  h_axes.SetMaximum((hists['data'].GetMaximum()+hists['data'].GetBinError(hists['data'].GetMaximumBin()))*10)
  h_axes.SetMinimum(0.01)
  pad1.SetLogy()
else:
  h_axes.SetMaximum((hists['data'].GetMaximum()+hists['data'].GetBinError(hists['data'].GetMaximumBin()))*1.3)
  h_axes.SetMinimum(0.)
h_axes.SetTitle("")
h_axes.GetXaxis().SetTitle("")
h_axes.GetXaxis().SetLabelSize(0)
h_axes.GetYaxis().SetTitleSize(0.05)
h_axes.GetYaxis().SetTitle("Events / GeV")
h_axes.GetYaxis().SetTitleOffset(1.1)
h_axes.GetYaxis().SetLabelSize(0.035)
h_axes.GetYaxis().SetLabelOffset(0.007)
h_axes.Draw()

leg0 = ROOT.TLegend(0.18,0.67,0.48,0.77)
leg0.SetFillStyle(0)
leg0.SetLineColor(0)
leg0.SetTextSize(0.04)
leg0.SetNColumns(2)
leg0.AddEntry(hists['data'],"Data","ep")
if doSignal: leg0.AddEntry(hists['spdf'],"S: #scale[0.9]{#sigma #bf{#it{#Beta}} = %.3f fb}"%limit,"fl")
leg0.Draw("Same")


leg = ROOT.TLegend(0.58,0.4,0.86,0.86)
leg.SetFillStyle(0)
leg.SetLineColor(0)
leg.SetTextSize(0.025)
#leg.AddEntry(hists['data'],"#scale[1.5]{Data}","ep")
#if doSignal: leg.AddEntry(hists['spdf'],"#scale[1.5]{S model}","fl")
#leg.AddEntry(0,"","")
for bname in bpdfs: 
  if "bern" in bname: fname = "#bf{Bernstein polynomial}"
  elif "exp" in bname: fname = "#bf{Sum of exponentials}"
  elif "pow" in bname: fname = "#bf{Sum of power law functions}"
  elif "lau" in bname: fname = "#bf{Laurent series}"
  elif "hmdijet" in bname: fname = "#bf{Dijet functions}"
  else: fname = "Unknown function"
  if bname == bpdf_bf_name: lstr = "#splitline{%s}{Order %s (Best fit)}"%(fname,bname[-1])
  else: lstr = "#splitline{%s}{Order %s}"%(fname,bname[-1])
  leg.AddEntry(hists[bname],lstr,"l")
leg.Draw("Same")

if doSignal:
  hists['spdf'].SetLineWidth(2)
  hists['spdf'].SetLineColor(9)
  hists['spdf'].SetFillColor(38)
  hists['spdf'].SetFillStyle(3001)
  hists['spdf'].GetXaxis().SetRangeUser(blindingRegion[0],blindingRegion[1])
  hists['spdf'].Draw("Hist same cf")

colourOptions=[1,2,3,4,5,6,7,8,9]
bnames = bpdfs.keys()
for bidx, bname in enumerate(bnames):
  hists[bname].SetLineWidth(2)
  hists[bname].SetLineColor( colourOptions[bidx] )
  hists[bname].Draw("HIST same C")
hists['data'].SetMarkerStyle(20)
hists['data'].SetMarkerColor(1)
hists['data'].SetLineColor(1)
if( opt.do_YToGG)&(( "cat0" in opt.cat )|( "cat1" in opt.cat )):
  hists['data'].SetLineColor(0)
else:
  hists['data'].Draw("Same PE")


# Add TLatex to plot
lat0 = ROOT.TLatex()
lat0.SetTextFont(42)
lat0.SetTextAlign(11)
lat0.SetNDC()
lat0.SetTextSize(0.06)
lat0.DrawLatex(0.12,0.92,"#bf{CMS} #it{Work in Progress}")
#lat0.DrawLatex(0.12,0.92,"#bf{CMS}")
lat0.DrawLatex(0.18,0.80,"#scale[0.75]{%s}"%Translate(cat,translateCats))

lat1 = ROOT.TLatex()
lat1.SetTextFont(42)
lat1.SetTextAlign(31)
lat1.SetNDC()
lat1.SetTextSize(0.06)
lat1.DrawLatex(0.9,0.92,"138 fb^{-1} (13 TeV)")

pad2.cd()
h_axes_ratio = hists_ratio['data'].Clone()
h_axes_ratio.Reset()
h_axes_ratio.SetMaximum((hists_ratio['data'].GetMaximum()+hists_ratio['data'].GetBinError(hists_ratio['data'].GetMaximumBin()))*1.3)
h_axes_ratio.SetMinimum((hists_ratio['data'].GetMinimum()-hists_ratio['data'].GetBinError(hists_ratio['data'].GetMinimumBin()))*1.2)
h_axes_ratio.SetTitle("")
h_axes_ratio.GetXaxis().SetTitleSize(0.05*padSizeRatio)
h_axes_ratio.GetXaxis().SetLabelSize(0.035*padSizeRatio)
h_axes_ratio.GetXaxis().SetLabelOffset(0.007)
h_axes_ratio.GetXaxis().SetTickLength(0.03*padSizeRatio)
h_axes_ratio.GetYaxis().SetLabelSize(0.035*padSizeRatio)
h_axes_ratio.GetYaxis().SetLabelOffset(0.007)
h_axes_ratio.GetYaxis().SetTitle("")
h_axes_ratio.Draw()

if doSignal:
  hsr = hists['spdf'].Clone()
  hsr.SetLineWidth(2)
  hsr.SetLineColor(9)
  hsr.SetFillColor(38)
  hsr.SetFillStyle(3001)
  hsr.GetXaxis().SetRangeUser(blindingRegion[0],blindingRegion[1])
  hsr.Draw("Hist same cf")

for bidx, bname in enumerate(bnames):
  hists_ratio[bname].SetLineWidth(2)
  hists_ratio[bname].SetLineColor( colourOptions[bidx] )
  hists_ratio[bname].Draw("HIST same C")
hists_ratio['data'].SetMarkerStyle(20)
hists_ratio['data'].SetMarkerColor(1)
hists_ratio['data'].SetLineColor(1)
if( opt.do_YToGG)&(( "cat0" in opt.cat )|( "cat1" in opt.cat )):
  hists_ratio['data'].SetLineColor(0)
else:
  hists_ratio['data'].Draw("Same PE")


# Add TLatex to ratio plot
lat2 = ROOT.TLatex()
lat2.SetTextFont(42)
lat2.SetTextAlign(33)
lat2.SetNDC(1)
lat2.SetTextSize(0.045*padSizeRatio)
lat2.DrawLatex(0.87,0.91,"Best fit B function subtracted")

ext_str = "_%s"%opt.ext if opt.ext != "" else ""
canv.Update()
canv.SaveAs("multipdf_plots_Oct22/bmodel_%s%s.pdf"%(cat,ext_str))
canv.SaveAs("multipdf_plots_Oct22/bmodel_%s%s.png"%(cat,ext_str))

