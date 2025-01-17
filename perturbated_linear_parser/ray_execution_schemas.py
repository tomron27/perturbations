import train_parser as tp
import optimal_noise_k_minus_1 as optimal_n
import k_minus_1_noise_maker as noise_maker
import mst_wrapper as mst_wrapper
import oracle_wrapper as oracle_wrapper
import ray

import utils
from globals import *


class exec_process_parallel():

    def __init__(self, create_files = False,is_train_dev_together = False, log_file_name = LOG_PATH+'log_process'):
        self.create_files =  create_files
        self.log_file_name = log_file_name

        if (os.path.isfile(log_file_name)):
            os.remove(log_file_name)

        logging.basicConfig(filename=self.log_file_name,
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)
        ray.init()

        logging.info('Execution started')
        if (self.create_files):
            logging.info('Strat creating per language files')
            utils.create_files_per_language_cross_lingual(num_sentences_per_lng_train = 1000, num_sentences_per_lng_dev = 100, is_train_dev_together = is_train_dev_together)
            logging.info('Finish creating per language files')

    @staticmethod
    @ray.remote
    def execute_parallel(language,eval_method='oracle',train_models = True,find_noise = True,is_oracle_inference_results=True,fixed_noise=False,noise_method='m'):
        if (train_models):
            logging.info('-'*50)
            logging.info('Training process started')
            tp.train_parser_all_lng(language)
            logging.info('Training process ended')

        if (find_noise):
            logging.info('-' * 50)
            logging.info('Optimal noise learning started')
            optimal_n.find_optimal_noise_per_language(eval_method=eval_method,specific_languages=language,noise_method=noise_method)
            logging.info('Optimal noise learning ended')

        logging.info('-' * 50)
        logging.info('Noised dependency trees creation started')
        noise_maker.create_noised_dps_over_all_languages(language,is_train_dev_together= False,k_best_baseline=False,fixed_noise=fixed_noise,noise_method=noise_method)
        logging.info('Noised dependency trees creation ended')


        logging.info('-' * 50)
        logging.info('mst wrapper started')
        mst_wrapper.mst_wrapper_for_all_languages(language,
                                                  final_file_name='UAS_perturbated_MLN_perturbated_after_predicted_pos',
                                                  is_train_dev_together=False,
                                                  is_mst=True,
                                                  given_one_file_repeated_sentnces=False,
                                                  remove_less_than_k_duplication=False)
        logging.info('mst wrapper ended')

        if (is_oracle_inference_results):
            logging.info('Oracle wrapper started')
            oracle_wrapper.oracle_wrapper_for_all_languages(language,final_file_name = 'UAS_perturbated_MLN_perturbated_after_predicted_pos' ,is_train_dev_together=False)
            logging.info('Oracle wrapper ended')

        return language+" is ready"


    @staticmethod
    @ray.remote
    def execute_parallel_baseline_1_max_tree(language,train_models = False,is_train_dev_together=True):
        if (train_models):
            logging.info('-'*50)
            logging.info('Training process started')
            tp.train_parser_all_lng(language,is_train_dev_together)
            logging.info('Training process ended')

        logging.info('-' * 50)
        logging.info('Noised dependency trees creation started')
        noise_maker.create_noised_dps_over_all_languages(language,is_train_dev_together)
        logging.info('Noised dependency trees creation ended')

        logging.info('-' * 50)
        logging.info('mst wrapper started')
        mst_wrapper.mst_wrapper_for_all_languages(language,
                                                  final_file_name='final_liang_1_best_after_predicted_pos',
                                                  is_train_dev_together=is_train_dev_together,
                                                  is_mst=False,
                                                  given_one_file_repeated_sentnces=False)
        logging.info('mst wrapper ended')

        return language+" is ready"



    @staticmethod
    @ray.remote
    def execute_parallel_baseline_k_best_trees(language,train_models = False,is_train_dev_together=True):
        if (train_models):
            logging.info('-'*50)
            logging.info('Training process started')
            tp.train_parser_all_lng(language,is_train_dev_together)
            logging.info('Training process ended')


        logging.info('-' * 50)
        logging.info('K-best (liang) dependency trees creation started')
        noise_maker.create_noised_dps_over_all_languages(specific_languages = language,
                                                         is_train_dev_together=True,
                                                         k_best_baseline = 100)
        logging.info('K-best (liang) dependency trees creation ended')


        logging.info('-' * 50)
        logging.info('mst wrapper started')
        mst_wrapper.mst_wrapper_for_all_languages(language,
                                                  final_file_name='UAS_liang_Kbest_baseline_k_100_after_predicted_pos',
                                                  is_train_dev_together = is_train_dev_together,
                                                  is_mst=True,
                                                  given_one_file_repeated_sentnces=True)
        logging.info('mst wrapper ended')

        logging.info('-' * 50)
        logging.info('Oracle wrapper started')
        oracle_wrapper.oracle_wrapper_for_all_languages(language,final_file_name = 'UAS_liang_Kbest_baseline_k_100_after_predicted_pos' ,is_train_dev_together=True)
        logging.info('Oracle wrapper ended')
        return language+" is ready"


class exec_process_single():

    def __init__(self, create_files=False, is_train_dev_together=False, log_file_name=LOG_PATH+'log_process'):
        self.create_files = create_files
        self.log_file_name = log_file_name

        if (os.path.isfile(log_file_name)):
            os.remove(log_file_name)

        logging.basicConfig(filename=self.log_file_name,
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

        logging.info('Execution started')
        if (self.create_files):
            logging.info('Strat creating per language files')
            utils.create_files_per_language_cross_lingual(num_sentences_per_lng_train=1000, num_sentences_per_lng_dev=100, is_train_dev_together=is_train_dev_together)
            logging.info('Finish creating per language files')

    @staticmethod
    def execute_single(language,eval_method='oracle', train_models=True, find_noise=True, is_oracle_inference_results=True, fixed_noise=False,noise_method='m'):

        if train_models:
            logging.info('-'*50)
            logging.info('Training process started')
            tp.train_parser_all_lng(language)
            logging.info('Training process ended')

        if find_noise:
            logging.info('-' * 50)
            logging.info('Optimal noise learning started')
            optimal_n.find_optimal_noise_per_language(eval_method=eval_method,specific_languages=language,noise_method=noise_method)
            logging.info('Optimal noise learning ended')

        # logging.info('-' * 50)
        # logging.info('Noised dependency trees creation started')
        # noise_maker.create_noised_dps_over_all_languages(language,is_train_dev_together= False,k_best_baseline=False,fixed_noise=fixed_noise,noise_method=noise_method)
        # logging.info('Noised dependency trees creation ended')
        #
        #
        # logging.info('-' * 50)
        # logging.info('mst wrapper started')
        # mst_wrapper.mst_wrapper_for_all_languages(language,
        #                                           final_file_name='UAS_perturbated_MLN_perturbated_after_predicted_pos',
        #                                           is_train_dev_together=False,
        #                                           is_mst=True,
        #                                           given_one_file_repeated_sentnces=False,
        #                                           remove_less_than_k_duplication=False)
        # logging.info('mst wrapper ended')

        if (is_oracle_inference_results):
            logging.info('Oracle wrapper started')
            oracle_wrapper.oracle_wrapper_for_all_languages(language,final_file_name = 'UAS_perturbated_MLN_perturbated_after_predicted_pos' ,is_train_dev_together=False)
            logging.info('Oracle wrapper ended')

        return language+" is ready"


    @staticmethod
    def execute_single_baseline_1_max_tree(language,train_models = False,is_train_dev_together=True):
        if (train_models):
            logging.info('-'*50)
            logging.info('Training process started')
            tp.train_parser_all_lng(language,is_train_dev_together)
            logging.info('Training process ended')

        logging.info('-' * 50)
        logging.info('Noised dependency trees creation started')
        noise_maker.create_noised_dps_over_all_languages(language,is_train_dev_together)
        logging.info('Noised dependency trees creation ended')

        logging.info('-' * 50)
        logging.info('mst wrapper started')
        mst_wrapper.mst_wrapper_for_all_languages(language,
                                                  final_file_name='final_liang_1_best_after_predicted_pos',
                                                  is_train_dev_together=is_train_dev_together,
                                                  is_mst=False,
                                                  given_one_file_repeated_sentnces=False)
        logging.info('mst wrapper ended')

        return language+" is ready"



    @staticmethod
    def execute_parallel_baseline_k_best_trees(language,train_models = False,is_train_dev_together=True):
        if (train_models):
            logging.info('-'*50)
            logging.info('Training process started')
            tp.train_parser_all_lng(language,is_train_dev_together)
            logging.info('Training process ended')


        logging.info('-' * 50)
        logging.info('K-best (liang) dependency trees creation started')
        noise_maker.create_noised_dps_over_all_languages(specific_languages = language,
                                                         is_train_dev_together=True,
                                                         k_best_baseline = 100)
        logging.info('K-best (liang) dependency trees creation ended')


        logging.info('-' * 50)
        logging.info('mst wrapper started')
        mst_wrapper.mst_wrapper_for_all_languages(language,
                                                  final_file_name='UAS_liang_Kbest_baseline_k_100_after_predicted_pos',
                                                  is_train_dev_together = is_train_dev_together,
                                                  is_mst=True,
                                                  given_one_file_repeated_sentnces=True)
        logging.info('mst wrapper ended')

        logging.info('-' * 50)
        logging.info('Oracle wrapper started')
        oracle_wrapper.oracle_wrapper_for_all_languages(language,final_file_name = 'UAS_liang_Kbest_baseline_k_100_after_predicted_pos' ,is_train_dev_together=True)
        logging.info('Oracle wrapper ended')
        return language+" is ready"

