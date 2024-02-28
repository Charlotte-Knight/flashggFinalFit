import ROOT
import sys
from tqdm import tqdm

ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.ERROR)

datacard = sys.argv[1]
f = ROOT.TFile(datacard)
w = f.Get("w")
CMS_channel = w.cat("CMS_channel")

f_in = ROOT.TFile(sys.argv[2])

CMS_hgg_mass = ROOT.RooRealVar("CMS_hgg_mass", "CMS_hgg_mass", 125)
#CMS_channel = None

datasets = []
skip_cats = []

for key in tqdm(f_in.GetListOfKeys()):
  toy_name = key.GetName()
  toy = f_in.Get(toy_name)

  # if CMS_channel is None:
  #   CMS_channel = ROOT.RooCategory("CMS_channel", "CMS_channel")
  #   for key in toy.GetListOfKeys():
  #     CMS_channel.defineType(key.GetName())

  import_pairs = []
  for key in toy.GetListOfKeys():
    tree_name = key.GetName() # also the category name
    if tree_name in skip_cats:
      continue
    elif CMS_channel.setLabel(tree_name) == True:
      skip_cats.append(tree_name)
      continue
        
    tree = toy.Get(tree_name)
    
    tree_data = ROOT.RooDataSet("data_%s"%tree_name, "data_%s"%tree_name, ROOT.RooArgSet(CMS_hgg_mass), ROOT.RooFit.Import(tree))
    import_pairs.append((tree_name, tree_data))

  imports = [ROOT.RooFit.Import(*import_pair) for import_pair in import_pairs]
  data = ROOT.RooDataSet("model_sData", "", ROOT.RooArgSet(CMS_hgg_mass), ROOT.RooFit.Index(CMS_channel), *imports)
  datasets.append([toy_name, data])

f_in.Close()

f_out = ROOT.TFile(sys.argv[3], "RECREATE")
f_out.mkdir("toys")
f_out.cd("toys")
for toy_name, dataset in datasets:
  dataset.Write(toy_name)
f_out.Close()