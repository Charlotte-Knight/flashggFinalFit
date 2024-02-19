#!/usr/bin/env bash

mx=$1
my=$2
mh=$3
m="mx${mx}my${my}"
mo="mx${mx}my${my}mh${mh}"

ABCD_C_var="ABCD_C"
ABCD_A_var="ABCD_A"

# ABCD_C_var="n_exp_binggttres${m}cat7_proc_dy_merged_hgg"
# ABCD_A_var="n_exp_binggttres${m}cat7_cr_proc_dy_merged_hgg"

combine --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -M MultiDimFit -m ${mh} -d Datacard_ggtt_resonant_${m}_ggtt_resonant.root -n _eff_check${mo}_ABCD_C --freezeParameters MH,MX,MY,r --setParameters MX=${mx},MY=${my},r=0 --algo grid -P ${ABCD_C_var} --points 20 --setParameterRanges ABCD_C=0,800

combine --redefineSignalPOI r --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_freezeDisassociatedParams --X-rtd MINIMIZER_multiMin_hideConstants --X-rtd MINIMIZER_multiMin_maskConstraints --X-rtd MINIMIZER_multiMin_maskChannels=2 -M MultiDimFit -m ${mh} -d Datacard_ggtt_resonant_${m}_ggtt_resonant.root -n _eff_check${mo}_ABCD_A --freezeParameters MH,MX,MY,r --setParameters MX=${mx},MY=${my},r=0 --algo grid -P ${ABCD_A_var} --points 20 --autoRange 3

workspace=higgsCombine_eff_check${mo}_VAR.MultiDimFit.mH${mh}.root
python get_veto_eff2.py $workspace > veto_eff_${mo}.txt
