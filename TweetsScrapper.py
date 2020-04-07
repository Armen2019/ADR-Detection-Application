import re
import json
import glob
import time
import pandas as pd
from subprocess import call
from langdetect import detect
from collections import OrderedDict


class TweetsScrapper:
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

    def create_command_line_from_each_drug_name(self, drug_names_list, start_date_in_func, end_date_in_func):
        """
        From each drug name create command line for scraping.
        """
        start_date_for_command_line = ' since:{}'.format(start_date_in_func)
        end_date_for_command_line_with_end_date = ' until:{}"'.format(end_date_in_func)
        for one_drug_name in drug_names_list:
            command_line_with_drug_name_without_date = 'scrapy crawl TweetScraper -a query="{}'.format(one_drug_name)
            final_command_line = command_line_with_drug_name_without_date + start_date_for_command_line + end_date_for_command_line_with_end_date
            call([final_command_line], shell=True)
            time.sleep(5)

    def from_json_to_df(self, path):
        """
        From json file create DataFrame.
        """
        tweet_files = glob.glob("{}".format(path))
        dict_list = []

        for json_file in tweet_files:
            with open(json_file, 'r') as jf:
                json_string = jf.read()
                json_dict = json.loads(json_string)
                dict_list.append(json_dict)
        df = pd.DataFrame(dict_list)
        df = df.replace({'\n': ' '}, regex=True)  # remove linebreaks in the dataframe
        df = df.replace({'\t': ' '}, regex=True)  # remove tabs in the dataframe
        final_df = df.replace({'\r': ' '}, regex=True)  # remove carriage return in the dataframe
        return final_df

    def without_replication(self, main_twits_text_df):
        """
        From annotated twits text dataset drop duplicates twits.
        :param main_twits_text_df
        :return:
            """
        all_twit_sort = main_twits_text_df.sort_values("text", ascending=False)
        all_twit_nodup = all_twit_sort.drop_duplicates(subset="text", keep="first")
        all_twit_nodup_sort_df = all_twit_nodup.sort_values("text", ascending=True)
        return all_twit_nodup_sort_df

    def filter_df(self, df_for_filtration, list_of_drug_names):
        """
        From annotated twits text extract and save texts with adr.
        :param
        :return:
        """
        filtered_tweet_list = []
        with_main_columns_df = df_for_filtration[["ID", "text", "url", "datetime"]]
        tweets_list = list(with_main_columns_df["text"])
        new_list_text_language = [tweets_list_1 for tweets_list_1 in tweets_list if
                                  detect(tweets_list_1) == "en"]
        new_list_text_len = [tweets_list_2 for tweets_list_2 in new_list_text_language if
                             4 <= len(tweets_list_2.split())]
        new_list_text_regex = [tweets_list_3 for tweets_list_3 in new_list_text_len
                               if not re.search(r'http://\w', tweets_list_3.lower())
                               and not re.search(r'https://\w', tweets_list_3.lower())
                               and not re.search(r'http://\s', tweets_list_3.lower())
                               and not re.search(r'https://\s', tweets_list_3.lower())]
        # return new_list_text_regex
        for tweet_text_4 in new_list_text_regex:
            if any(drug_names.lower() in tweet_text_4.lower() for drug_names in list_of_drug_names):
                filtered_tweet_list.append(tweet_text_4)
        filtered_tweet_df = pd.DataFrame(filtered_tweet_list, columns=["text"])
        return filtered_tweet_df

    def merge_main_df_with_filtered_df(self, filtered_df, without_repl_df):
        """
        Filtered tweets merge with main DataFrame.
        """
        df1_sort = filtered_df.sort_values("text", ascending=True)
        df2_sort = without_repl_df.sort_values("text", ascending=True)
        merged = pd.merge(df1_sort, df2_sort, on="text")
        return merged

