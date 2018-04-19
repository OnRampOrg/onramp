#!/usr/bin/env python

#
# Curriculum Module Run Script
# - Run once per run of the module by a user
# - Run inside job submission. So in an allocation.
# - onramp_run_params.cfg file is available in current working directory
#
import os
import sys
from subprocess import call, CalledProcessError, check_call
from configobj import ConfigObj

#
# Read the configobj values
#
# This will always be the name of the file, so fine to hardcode here
conf_file = "onramp_runparams.cfg"
# Already validated the file in our onramp_preprocess.py script - no need to do it again
config    = ConfigObj(conf_file)

#
# Run my program
#
os.chdir('src')

# Retrive mode
mode = config['monte_carlo']['mode']

def default_case():
    print  mode + ' is not a recognized mode.\n'
    print '+----------------------------+\n'
    print '| mode | program             |\n'
    print '+----------------------------+\n'
    print '|  1s  | coin_flip_seq       |\n'
    print '|  1p  | coin_flip_omp       |\n'
    print '|  2s  | draw_four_suits_seq |\n'
    print '|  2p  | draw_four_suits_omp |\n'
    print '|  3s  | roulette_sim_seq    |\n'
    print '|  3p  | roulette_sim_omp    |\n'
    print '+----------------------------+\n'
    sys.exit(-1)

def coin_seq():
    call(['mpirun', '-np', '1', 'coin_flip_seq'])

def coin_omp():
    call(['mpirun', '-np', '1', 'coin_flip_omp', config['monte_carlo']['threads']])

def draw_seq():
    call(['mpirun', '-np', '1', 'draw_four_suits_seq'])

def draw_omp():
    call(['mpirun', '-np', '1', 'draw_four_suits_omp', config['monte_carlo']['threads']])

def roulette_seq():
    call(['mpirun', '-np', '1', 'roulette_sim_seq'])

def roulette_omp():
    call(['mpirun', '-np', '1', 'roulette_sim_omp', config['monte_carlo']['threads']])

def pi_seq():
    call(['mpirun', '-np', '1', 'pi_seq', config['monte_carlo']['pi_trials']])

def pi_omp():
    call(['mpirun', '-np', '1', 'pi_omp', config['monte_carlo']['pi_trials'], config['monte_carlo']['threads']])

executables = { '1s' : coin_seq, '1p' : coin_omp, '2s' : draw_seq, '2p' : draw_omp, '3s' : roulette_seq, '3p' : roulette_omp, '4s' : pi_seq, '4p' : pi_omp}

executables.get(mode, default_case)()

# Exit 0 if all is ok
sys.exit(0)
