"""
Words misspelling generator class​
"""
import re
from collections import defaultdict

import Levenshtein
import pandas as pd
from gensim.models import KeyedVectors


class MisspelGen:
    def __init__(self):
        pass

    def generate_spelling_variants(self, seedwordlist, word_vectors, semantic_search_length=500,
                                   levenshtein_threshold=0.85, setting=1):
        """
            setting -> 0 = weighted levenshtein ratios
                    -> 1 = standard levenshtein ratios
    ​
        :param seedwordlist:            list of words for which spelling variants are to be generated
        :param word_vectors:            the word vector models
        :param semantic_search_length:  the number of semantically similar terms to include in each iteration
        :param levenshtein_threshold:   the threshold for levenshtein ratio
    ​
        :return: dictionary containing the seedwords as key and all the variants as a list of values
    ​
        """
        seq_score = None
        vars = defaultdict(list)
        for seedword in seedwordlist:
            # a dictionary to hold all the variants, key: the seedword, value: the list of possible misspellings
            # a dynamic list of terms that are still to be expanded
            terms_to_expand = []
            terms_to_expand.append(seedword)
            all_expanded_terms = []
            level = 1
            while len(terms_to_expand) > 0:
                t = terms_to_expand.pop(0)
                all_expanded_terms.append(t)
                try:
                    similars = word_vectors.most_similar(t, topn=semantic_search_length)
                    for similar in similars:
                        similar_term = similar[0]
                        if setting == 1:
                            seq_score = Levenshtein.ratio(str(similar_term), seedword)
                        if setting == 0:
                            seq_score = self.weighted_levenshtein_ratio(str(similar_term), seedword)
                        if seq_score > levenshtein_threshold:
                            if not re.search(r'\_', similar_term):
                                vars[seedword].append(similar_term)
                                if not similar_term in all_expanded_terms and not similar_term in terms_to_expand:
                                    terms_to_expand.append(similar_term)
                except:
                    pass
                level += 1
            vars[seedword] = list(set(vars[seedword]))
        return vars

    def weighted_levenshtein_ratio(self, variant, seedword):
        """
        Given a possible variant and a seedword, returns the weighted average levenshtein ratio for the pair
        :param variant:
        :param seedword:
        :return:
        """
        weights = {0.5: 1.0133116199788939,
                   0.7: 0.97859255044477178,
                   0.9: 0.94999999999999996,
                   0.3: 1.05,
                   0.1: 0.99601150272112082}
        l_ratio_vals = []
        window_beg = 0
        window_end = int((len(seedword) - 1) / 2)
        if len(variant) < len(seedword):
            variant = self.pad(variant, len(seedword))
        elif len(seedword) < len(variant):
            seedword = self.pad(seedword, len(variant))
        while window_end <= len(seedword) and window_end <= len(variant):
            relpos = ((window_beg + window_end + 0.) / 2.) / len(seedword)
            if relpos < 0.2:
                relpos = 0.1
            elif relpos < 0.4:
                relpos = 0.3
            elif relpos < 0.6:
                relpos = 0.5
            elif relpos < 0.8:
                relpos = 0.7
            elif relpos < 1.0:
                relpos = 0.9
            levenshtein_ratio = Levenshtein.ratio(seedword[window_beg:window_end], variant[window_beg:window_end])
            levenshtein_ratio_weighted = weights[relpos] * levenshtein_ratio
            l_ratio_vals.append(levenshtein_ratio_weighted)
        window_beg += 1
        window_end += 1
        average_weighted_levenshtein_ratio = sum(l_ratio_vals) / len(l_ratio_vals)
        return average_weighted_levenshtein_ratio

    def pad(self, drugname, required_length):
        """
        Helper function for padding terms when computing weighted Levenshtein Ratio
        """
        post_padding = ''
        for i in range(0, required_length):
            if i < len(drugname):
                post_padding += drugname[i]
            else:
                post_padding += '?'
        return post_padding

    def load_vector_model(self, filename):
        """
            Loads and returns a word2vec vector models
            :param filename: the filename for the models
            :return: the loaded models
        """
        print('loading models this may take a while')
        word_vectors = KeyedVectors.load_word2vec_format(filename, binary=True, encoding='utf8',
                                                         unicode_errors='ignore')
        return word_vectors

    def create_drug_name_list(self, path_of_drug_name_file: str):
        """
        Create a list from drug names and their synonyms
        :param path_of_drug_name_file:
        :return:
        """

        drug_bank_drug_names = pd.read_csv(path_of_drug_name_file, sep='\t', encoding='utf-8')
        drug_name_list = list(drug_bank_drug_names["Drug name"])
        new_drug_list = [drug_name.lower() for drug_name in drug_name_list]
        return new_drug_list

    def misspeling(self, drug):
        weights = {0.5: 1.0133116199788939,
                   0.7: 0.97859255044477178,
                   0.9: 0.94999999999999996,
                   0.3: 1.05,
                   0.1: 0.99601150272112082}

        # SET THE LEVENSHTEIN RATIO THRESHOLD
        lt = 0.85  # lower this to increase recall and decrease precision
        # lt = 0.7  # lower this to increase recall and decrease precision

        # SET THE NUMBER OF SEMANTICALLY SIMILAR TERMS TO INCLUDE IN EACH ITERATION
        ssl = 4000
        df2 = pd.DataFrame({"Drug name": [drug]})
        df2.to_csv('Data/tweetRequest.csv', mode='w', index=False)

        word_vectors_path = "Data/trig-vectors-phrase.bin"

        generic_drug_names_file_path = "Data/tweetRequest.csv"

        all_generated_words_saving_path = "Data/misspellings.csv"

        misspel = MisspelGen()

        word_vectors = misspel.load_vector_model(word_vectors_path)

        seedwordlist = misspel.create_drug_name_list(generic_drug_names_file_path)

        # DEFAULT SETTING
        spelling_variants_default = misspel.generate_spelling_variants(seedwordlist[0:14], word_vectors,
                                                                       semantic_search_length=ssl,
                                                                       levenshtein_threshold=lt,
                                                                       setting=1)

        df_generated_misspelled_words = pd.DataFrame(list(spelling_variants_default.items()),
                                                     columns=['General Drug Name', 'Generated Drug Names'])
        misspelled_list = list(df_generated_misspelled_words["Generated Drug Names"])
        df_generated_misspelled_words["Generated Drug Names"] = [
            str(misspelled_name).strip('[]').strip("'").replace("'", "") for misspelled_name in misspelled_list]
        df_generated_misspelled_words.to_csv(all_generated_words_saving_path, sep='\t', encoding='utf-8', index=False)
