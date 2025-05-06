#!/bin/sh  

#$ -N new_era
#$ -pe openmpi 1
#$ -P ap
#$ -q ap-test.q
#$ -o /dev/null
#$ -e /dev/null


## Execute python script with VERTICAL EMITTANCE, RUN NUMBER, NUMBER OF SAMPELS
/home/exr35747/.python/bin/python3.10 /dls/physics/exr35747/my_own_elegant/TL/lifetime_emit_script.py $1 $2 $3
