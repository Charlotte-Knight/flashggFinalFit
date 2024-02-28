import pandas as pd
import tools.writeToDatacard as td

columns = ["prune", "cat", "proc", "modelWSFile", "model", "rate", "lumi_13TeV_Uncorrelated_2016", "lumi_13TeV_Uncorrelated_2017", "lumi_13TeV_Uncorrelated_2018", "lumi_13TeV_Correlated", "lumi_13TeV_Correlated_1718", "PreselSF_2016", "PreselSF_2017", "PreselSF_2018"]
rows = [[0, "cat0", "sig0", "my_ws_file.root", "my_model", 36000, '-', '-', '-', '-', '-', [1/1.05,1.05], "-", "-"]]
data = pd.DataFrame(rows, columns=columns)
print(data)

class Options:
  def __init__(self):
    self.years = '2016,2017,2018'
    self.doSTXSMerging = False
    self.doSTXSScaleCorrelationScheme = False
opt=Options()

experimental_systematics = [
                # Updated luminosity partial-correlation scheme: 13/5/21 (recommended simplified nuisances)
                {'name':'lumi_13TeV_Uncorrelated','title':'lumi_13TeV_Uncorrelated','type':'constant','prior':'lnN','correlateAcrossYears':0,'value':{'2016':'1.010','2017':'1.020','2018':'1.015'}},
                {'name':'lumi_13TeV_Correlated','title':'lumi_13TeV_Correlated','type':'constant','prior':'lnN','correlateAcrossYears':-1,'value':{'2016':'1.006','2017':'1.009','2018':'1.020'}},
                {'name':'lumi_13TeV_Correlated_1718','title':'lumi_13TeV_Correlated_1718','type':'constant','prior':'lnN','correlateAcrossYears':-1,'value':{'2016':'-','2017':'1.006','2018':'1.002'}},
                {'name':'PreselSF','title':'CMS_hgg_PreselSF','type':'factory','prior':'lnN','correlateAcrossYears':0},
              ]

with open("test_datacard.txt", "w") as fdata:
  td.writePreamble(fdata, opt)
  td.writeProcesses(fdata,data,opt)
  for syst in experimental_systematics:
    td.writeSystematic(fdata,data,syst,opt)