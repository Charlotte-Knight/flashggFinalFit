# Config file: options for signal fitting

backgroundScriptCfg = {
  
  # Setup
  #'inputWSDir':'/home/hep/mdk16/PhD/ggtt/CMSSW_10_2_0/src/HHToGGTT/output_trees/ws/data_2018/', # location of 'allData.root' file
  #'inputWSDir':'/home/hep/mdk16/PhD/ggtt/ParamNN/outputTrees/ws/data_2018/',
  'inputWSFile':'<trees/year/m/ws/signal_year>/allData.root',
  'cats':'auto', # auto: automatically inferred from input ws
  'ext':'ggtt_resonant_<signal_year>_<m>', # extension to add to output directory
  'year':'<signal_year>', # Use combined when merging all years in category (for plots)

  # Job submission options
  'batch':'IC', # [condor,SGE,IC,local]
  #'batch':'local',
  'queue':'hep.q' # for condor e.g. microcentury
  
}
