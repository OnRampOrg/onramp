#!/bin/bash
#PBS -N pbstest
#PBS -m abe
#PBS -l nodes=1:ppn=2,pmem=512mb
#PBS -l walltime=00:10:00
#PBS -o output
#PBS -j oe
#PBS -V

cd ~/HPL-benchmark/hpl-2.0/bin/BCCD

mpirun -np 12 -machinefile $PBS_NODEFILE ./xhpl

date
