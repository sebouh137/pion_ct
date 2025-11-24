#!/bin/bash
#SBATCH --job-name=beagle
#SBATCH --array=0-159       # 160 jobs
#SBATCH --output=/volatile/spaul/pion_ct/logs/job_%A_%a.out
#SBATCH --error=/volatile/spaul/pion_ct/logs/job_%A_%a.err

# run this file via sbatch slurm_beagle.sh

set -euo pipefail

# Example: decode array ID → (i, targ, j)
files_per_setting=10
targs=(1H 2H 12C 63Cu)
Q2s=("5.0" "6.5" "8.5" "7.5")

task_id=$SLURM_ARRAY_TASK_ID

i=$(( task_id / (4 * files_per_setting) ))
rem=$(( task_id % (4 * files_per_setting) ))
targ_index=$(( rem / files_per_setting ))
j=$(( rem % files_per_setting + 1 ))

targ=${targs[$targ_index]}
Q2=${Q2s[$i]}


source SDCC_setup.sh
source beagle_setup.sh
mkdir parsed


tmpdir=/volatile/hallc/spaul/pion_ct/${targ}_${Q2}_${j}/
mkdir -p $tmpdir
cp nuclear.bin fort.* eAsnoq input/${targ}_${Q2}.inp $tmpdir

cd $tmpdir
$BEAGLESYS/BeAGLE < ${targ}_${Q2}.inp
cd -
python parse_multihadron.py $tmpdir/OUTFILE.txt parsed/${targ}_${Q2}_${j}.csv $i $targ





