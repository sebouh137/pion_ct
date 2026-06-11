#!/bin/bash

for task_id in {0..159}; do

files_per_setting=10
targs=(1H 2H 12C 63Cu)
Q2s=("5.0" "6.5" "8.5" "7.5")

#task_id=$SLURM_ARRAY_TASK_ID

i=$(( task_id / (4 * files_per_setting) ))
rem=$(( task_id % (4 * files_per_setting) ))
targ_index=$(( rem / files_per_setting ))
j=$(( rem % files_per_setting + 1 ))

targ=${targs[$targ_index]}
Q2=${Q2s[$i]}

#cd /home/spaul/pion_ct/beagle
#source SDCC_setup.sh
#source beagle_setup.sh
#mkdir parsed


tmpdir=/work/hallc/e1206107/spaul/pion_ct/beagle_output/${targ}_${Q2}_${j}/
#mkdir -p $tmpdir
#cp nuclear.bin fort.* eAS1noq input/${targ}_${Q2}.inp $tmpdir

#cd $tmpdir
#$BEAGLESYS/BeAGLE < ${targ}_${Q2}.inp
#cd -
python parse_multihadron.py $tmpdir/OUTFILE.txt parsed/${targ}_${Q2}_${j}.csv $i $targ &

if (( task_id % 50 == 0 )); then
    wait
fi

done
wait


