#!/usr/bin/env bash

set -e

cd /home/hep/mdk16/PhD/ggtt/finalfits_try2/CMSSW_10_2_13/src/flashggFinalFit

source /cvmfs/cms.cern.ch/cmsset_default.sh
source /vols/grid/cms/setup.sh
source setup.sh

sig_model=$1
nCats=$2
m=$3
sig_years="$4 $5 $6"

get_last_cat() {
  for cat in $(grep "bin " $1 ) ; do
    last_cat=$cat
  done
  echo $last_cat
}

pushd Datacard
  python makeDatacardGGTT_combined.py $sig_model $nCats $m $sig_years > Datacard_ggtt_resonant_${m}_all_cats.txt
  # echo "signal_scaler rateParam * ggttres* 0.001" >> Datacard_ggtt_resonant_${m}.txt
  # echo "nuisance edit freeze signal_scaler" >> Datacard_ggtt_resonant_${m}.txt
  # echo "res_bkg_scaler rateParam * res_bkg* 1" >> Datacard_ggtt_resonant_${m}.txt
  # echo "nuisance edit freeze res_bkg_scaler" >> Datacard_ggtt_resonant_${m}.txt

  combineCards.py --xc=$(get_last_cat Datacard_ggtt_resonant_${m}_all_cats.txt) Datacard_ggtt_resonant_${m}_all_cats.txt > Datacard_ggtt_resonant_${m}.txt
popd