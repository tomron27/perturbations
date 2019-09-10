import train_parser as tp
import optimal_noise_k_minus_1 as optimal_n
import k_minus_1_noise_maker as noise_maker
import mst_wrapper as mst_wrapper
import oracle_wrapper as oracle_wrapper
from ray_execution_schemas import exec_process_parallel, exec_process_single
import logging
import os
import ray
import sys
import argparse

import utils
from globals import *


parser = argparse.ArgumentParser()
parser.add_argument('--train_dev_together',action='store_true')
parser.add_argument('--baseline',default='k_best')
parser.add_argument('--create_files',action='store_true')
parser.add_argument('--train_models',action='store_true')
parser.add_argument('--dont_find_noise',action='store_true')

parser.add_argument('--fixed_noise',default=False)
parser.add_argument('--noise_method',default='m')

args = parser.parse_args()

train_dev_together = args.train_dev_together #False
baseline = args.baseline #'k_best' ,None,'1_best'
create_files = args.create_files
train_models = args.train_models
fixed_noise = args.fixed_noise
noise_method = args.noise_method
find_noise = not (args.dont_find_noise)

exec_process_obj = exec_process_parallel(create_files=create_files, is_train_dev_together = train_dev_together)

if (train_dev_together):
    model_dir_prefix = BASELINE_TRAIN_DEV_PREFIX
    language_dirs = [lng for lng in os.listdir(DATA) if lng.startswith(model_dir_prefix) and lng.split('_')[1]]
    if (baseline =='1_best'):
        all_ready_lng = ray.get([exec_process_obj.execute_parallel_baseline_1_max_tree.remote(language) for language in language_dirs])
    elif (baseline=='k_best'):
        all_ready_lng = ray.get([exec_process_obj.execute_parallel_baseline_k_best_trees.remote(language,train_models = train_models) for language in language_dirs])
else:
    model_dir_prefix = UD_PREFIX
    language_dirs = [lng for lng in os.listdir(DATA) if lng.startswith(model_dir_prefix) and lng.split('_')[1]]
    # all_ready_lng = ray.get([exec_process_obj.execute_parallel.remote(language,
    #                                                            eval_method='oracle',
    #                                                            train_models=train_models,
    #                                                            find_noise=find_noise,
    #                                                            is_oracle_inference_results=True,
    #                                                            fixed_noise=fixed_noise,
    #                                                            noise_method=noise_method) for language in language_dirs])

    # DEBUG - sequential execution
    for language in language_dirs:
        exec_process_single.execute_single(language, eval_method='oracle', train_models=train_models, find_noise=find_noise,
                         is_oracle_inference_results=True, fixed_noise=fixed_noise, noise_method=noise_method)
