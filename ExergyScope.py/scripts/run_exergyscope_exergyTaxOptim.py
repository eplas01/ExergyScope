# -*- coding: utf-8 -*-
"""
This script modifies the input data and runs the ExergyScope model

@author: Paolo Thiran, Matija Pavičević, Xavier Rixhon, Gauthier Limpens
"""

import os
from pathlib import Path

import numpy as np

import exergyscope as es

if __name__ == '__main__':
    analysis_only = False
    compute_TDs = True
    for i in np.arange(0, 3, 0.1):
        #for j in np.arange(0, 2, 0.1):
            # loading the config file into a python dictionnary
            config = es.load_config(config_fn='config_ref.yaml')
            config['Working_directory'] = os.getcwd() # keeping current working directory into config

            # Reading the data of the csv
            es.import_data(config)

            config['exergy']=0#i
            config['NR_cost']=0#j
            config['carbon_cost']=i
            if compute_TDs:
                es.build_td_of_days(config)

            if not analysis_only:
                # Printing the .dat files for the optimisation problem
                es.print_data(config)

                # Running EnergyScope
                es.run_es(config)