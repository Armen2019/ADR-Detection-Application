import glob
import os
import os.path
import shutil
from collections import OrderedDict
from os import path

import pandas as pd

from Generator.misspelling_generator import MisspelGen
from TwiitsPreprocessing import TwiitsPreprocessing


class ScrapingUtils:

    def create_command_line_from_each_drug_name(self, drug_names_list, start_date_in_func, end_date_in_func):
        """
        From each drug name create command line for scraping.
        """

        start_date_for_command_line = ' since:{}'.format(start_date_in_func)
        end_date_for_command_line_with_end_date = ' until:{}"'.format(end_date_in_func)
        for one_drug_name in drug_names_list:
            command_line_with_drug_name_without_date = 'scrapy crawl TweetScraper -a query="{}'.format(one_drug_name)
            final_command_line = command_line_with_drug_name_without_date + start_date_for_command_line + end_date_for_command_line_with_end_date
            os.system(final_command_line)

    def create_drug_name_list_syn(self, path_of_drug_name_file: str):
        """
        Create a list from drug names and their synonyms
        :param path_of_drug_name_file:
        :return:
        """
        drug_list_generated = []
        drug_bank_drug_names = pd.read_csv(path_of_drug_name_file, sep='\t', encoding='utf-8')
        general_drug_name_list = list(drug_bank_drug_names["General Drug Name"])
        generated_drug_names_list = list(drug_bank_drug_names["Generated Drug Names"])
        generated_drug_names_list_without_nan = [x for x in generated_drug_names_list if str(x) != "nan"]
        for drug in generated_drug_names_list_without_nan:
            drug_list_generated.extend(drug.split(", "))
        final_drug_names_list = general_drug_name_list + drug_list_generated
        drug_list = list(OrderedDict.fromkeys(final_drug_names_list))
        return drug_list

    def search_tweet(self, tweet, start_date, end_date):
        if str(path.exists('Data/tweet')):
            shutil.rmtree('Data/tweet')
        misspelling = MisspelGen()
        misspelling.misspeling(tweet)
        generic_and_generated_drug_names_file_path = "Data/misspellings.csv"

        drug_names_list = self.create_drug_name_list_syn(generic_and_generated_drug_names_file_path)

        self.create_command_line_from_each_drug_name(drug_names_list, start_date, end_date)

        self.from_json_to_excel()

        prep = TwiitsPreprocessing()
        prep.pre_process()

    def tweets_sentiment_vector(self, sentiments):
        file_name = 'Data/output.xlsx'
        df = pd.read_excel(file_name)
        df['sentiments'] = sentiments
        df.to_excel('Data/output.xlsx', index=False)

    def from_json_to_excel(self):
        pd.set_option('display.max_columns', None)

        temp = pd.DataFrame()

        path_to_json = 'Data/tweet/*'

        json_pattern = os.path.join(path_to_json)
        file_list = glob.glob(json_pattern)
        dfs = []
        for file in file_list:
            dfs.append(pd.read_json(file, lines=True))

        big_frame = pd.concat(dfs, ignore_index=True, axis=0)
        new_data = big_frame[['text']]

        new_data.to_excel('Data/output.xlsx', index=False, header=True)
