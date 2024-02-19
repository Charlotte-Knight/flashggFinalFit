import ROOT
import sys

in_file = sys.argv[1]
out_file = sys.argv[2]

f = ROOT.TFile(in_file)
w = f.Get("multipdf")
w.Print()

x = w.var("CMS_hgg_mass")
original_shape = w.pdf("CMS_hgg_ggttresmx320my60cat2_combined_13TeV_bkgshape")
original_shape.SetName("original_shape")
original_shape.SetTitle("original_shape")

generic = ROOT.RooGenericPdf("generic", "(@0 < 120) ? 1 : (0.001 + exp(-(@0-120))) ", ROOT.RooArgList(x))
bkg_prod = ROOT.RooProdPdf("CMS_hgg_ggttresmx320my60cat2_combined_13TeV_bkgshape", "CMS_hgg_ggttresmx320my60cat2_combined_13TeV_bkgshape", ROOT.RooArgList(original_shape, generic))

# uniform = ROOT.RooUniform("uniform", "uniform", ROOT.RooArgSet(x))
# heaviside = ROOT.RooStats.Heaviside("heaviside", "heaviside", x, ROOT.RooFit.RooConst(115))
# heaviside_pdf = ROOT.RooAbs
# pdf_sum = ROOT.RooAddPdf("pdf_sum", "pdf_sum", uniform, heaviside, ROOT.RooFit.RooConst(0.01))
# bkg_prod = ROOT.RooProdPdf("bkg_prod", "bkg_prod", ROOT.RooArgList(original_shape, pdf_sum))

x.setVal(114)
print(bkg_prod.getVal())
x.setVal(116)
print(bkg_prod.getVal())

imp = getattr(w, "import")

#imp(original_shape)
imp(bkg_prod)

w.writeToFile(out_file)