#!/usr/bin/env bash

set -e

cd /home/hep/mdk16/PhD/ggtt/finalfits_try2/CMSSW_10_2_13/src/flashggFinalFit

source /cvmfs/cms.cern.ch/cmsset_default.sh
source /vols/grid/cms/setup.sh
source setup.sh

mggl=$1
mggh=$2
mx=$3
my=$4
mh=$5

m="mx${mx}my${my}"
mo="mx${mx}my${my}mh${mh}"

pushd Combine
  text2workspace.py Datacard_ggtt_resonant_${m}.txt -o Datacard_ggtt_resonant_${m}_ggtt_resonant.root -m $mh higgsMassRange=${mggl},${mggh}
popd