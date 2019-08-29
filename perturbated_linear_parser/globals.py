import os
from os.path import join
import logging

BASE_DIR = "/home/tomron27@st.technion.ac.il/projects/perturbations/"
DATA = join(BASE_DIR, "data")
NOISED_LIST_DIR_NAME = 'noised_list'
RESULTS_DIR = join(DATA, 'results')
UNIVERSAL_DEP_DIR = 'Universal_Dependencies_2.0'
UD = join(DATA, UNIVERSAL_DEP_DIR)
log = logging.getLogger(__name__)

