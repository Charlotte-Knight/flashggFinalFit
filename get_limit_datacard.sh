#!/usr/bin/env bash

set -e

cd /home/hep/mdk16/PhD/ggtt/finalfits_try2/CMSSW_10_2_13/src/flashggFinalFit

source /cvmfs/cms.cern.ch/cmsset_default.sh
source /vols/grid/cms/setup.sh
source setup.sh

sig_model=$1
res_bkg_model=$2
m=$3
mh=$4
mx=$5
my=$6
dy_bkg_model=$7

m="mx${mx}my${my}"
mo="mx${mx}my${my}mh${mh}"

get_last_cat() {
  for cat in $(grep "bin " $1 ) ; do
    last_cat=$cat
  done
  echo $last_cat
}

pushd Datacard
  if [[ -n $dy_bkg_model ]]; then 
    python makeDatacardGGTT_new.py -o Datacard_ggtt_resonant_${m}.txt --MH $mh --MX $mx --MY $my --prune --sig-syst ${sig_model}/systematics.json --res-bkg-syst ${res_bkg_model}/systematics.json --do-res-bkg --doABCD
  else
    python makeDatacardGGTT_new.py -o Datacard_ggtt_resonant_${m}.txt --MH $mh --MX $mx --MY $my --prune --sig-syst ${sig_model}/systematics.json --res-bkg-syst ${res_bkg_model}/systematics.json --do-res-bkg
  fi
popd