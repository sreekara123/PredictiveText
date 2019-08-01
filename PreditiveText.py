import re
import statistics

def read_data(filename=""):
    """
    :param filename: name of the file to read
    :except invalid file
    :return: list: list of all the lines in the file
    """
    try:
        # read all the lines of the file
        if not isinstance(filename, str):
            raise Exception
        f = open(filename, 'r')
        lines_read = f.readlines()
        f.flush()
        f.close()
        return lines_read
    except:
        print("invalid file")
        return []


def clean_data(my_data=1):
    """

    :param my_data: list of lines to clean
    :except my_data contains something which is not string
    :return: list: cleaned data
    """
    try:
        i = 0
        for line in my_data:
            line = " " + line
            line = line + " "
            # 2 or more hyphens case
            line = re.sub(r"([\w])(-{2,})([\w])", r"\1 \3", line)
            # hyphen case
            line = re.sub(r"([\w])(-)([\w])", r"\1\3", line)
            # remove all non alphanumerics except '
            line = re.sub(r"[^ \w\']", "", line)
            # remove '_'
            line = re.sub(r"[_]", "", line)
            # prefix num case
            line = re.sub(r"([ ])(\d+\.*\d*)([^ \t\d])", r" \2 \3", line)
            # suffix num case
            line = re.sub(r"([^ \t\d]*)(\d+\.*\d*)([ ])", r"\1 \2 ", line)
            # number identifier
            line = re.sub('(\d*[.]\d+)?[\d]+ ', 'num ', line)
            # make all nums in a row to one num
            line = re.sub(r"(num {1,}){1,}", "num ", line)
            # make 2 or spaces into 1
            line = re.sub(r"[ ]{2,}", " ", line)
            line = line.lstrip()
            line = line.rstrip()
            line = line.lower()
            my_data[i] = line
            i += 1

        return my_data
    except:
        print "inavalid data"
        return []


def build_n_gram_dict(n="", cleaned_data=""):
    """

    :param n: the gram dictionary to build
    :param cleaned_data:  the cleaned data to add into the dictionary
    :except invalid n or cleaned data
    :return: dictionary: words and frequencies in n-gram
    """

    try:
        str = ""
        map = {}
        # go through each line of cleaned data to build the dictionary
        for line in cleaned_data:
            tokens = line.split(" ")  # split the line by space
            tokens.insert(0, '<s>')
            for i in range(len(tokens) - n+1):
                for j in range(n-1):
                    str = str + tokens[i+j] + " "
                str = str + tokens[i+n-1]
                if str in map:
                    val = map.get(str)
                    val += 1
                    map[str] = val
                else:
                    map[str] = 1
                str = ""

        return map
    except:
        print "inavlid data passed"
        return {}


def calculate_PP(test_sentences="", ngram_models=""):
    """

    :param test_sentences: list of sentences for which we have to calculate perplexity
    :param ngram_models: all n gram dictionaries (1 gram, 2 gram,..., n gram)
    :except not a list of strings, ngram models
    :return: double: the mean perplexity of test_sentences
    """

    try:
        pp_list = []
        n = max(ngram_models, key=int)
        V = len(ngram_models[1].keys())
        sum_values = sum(ngram_models[1].values())
        # 1 gram dictionary is the only dict then just take count(words)/count(dict)
        if n == 1:
            for line in test_sentences:
                line_prob = 1.0
                tokens = line.split()
                tokens.insert(0, '<s>')
                for word in tokens:
                    line_prob *= float((ngram_models.get(1).get(word, 0)+1)) / (sum_values + V)
                inverse_words = 1.0 / len(tokens)
                line_prob = pow(1 / line_prob, inverse_words)
                pp_list.append(line_prob)
            average_pp = statistics.mean(pp_list)
            return average_pp

        for line in test_sentences:
            line_prob = 1.0
            tokens = line.split()
            tokens.insert(0, '<s>')
            for i in range(1, len(tokens)):
                count_num = 0
                count_den = 0
                sent = ""
                if i < n:
                    for j in range(i):
                        sent += tokens[j] + " "
                    sent += tokens[i]

                    count_num = ngram_models.get(i+1).get(sent, 0)
                    sent = ""
                    for j in range(i-1):
                        sent += tokens[j] + " "
                    sent += tokens[i-1]
                    count_den = ngram_models.get(i).get(sent, 0)
                    # print 'num: ', count_num+1, ' den: ', count_den+V

                elif i >= n:
                    sent = ""
                    for j in range(i-n+1, i):
                        sent += tokens[j] + " "
                    sent += tokens[i]
                    count_num = ngram_models.get(n).get(sent, 0)
                    sent=""
                    for j in range(i-n+1, i-1):
                        sent += tokens[j] + " "
                    sent += tokens[i-1]
                    count_den = ngram_models.get(n-1).get(sent, 0)
                    # print 'num: ', count_num+1, ' den: ', count_den+V

                line_prob *= float((count_num + 1))/(count_den + V)
            inverse_words = 1.0 / len(tokens)
            # print inverse_words
            # print line_prob
            line_prob = pow(1 / line_prob, inverse_words)
            pp_list.append(line_prob)

        average_pp = statistics.mean(pp_list)
        return average_pp
    except:
        print ("invalid data passed")
        return -1


def generate_text(ngram_models="", text_length="", seed_word=""):
    """

    :param ngram_models: all n n_gram_models
    :param text_length: length of text to generate
    :param seed_word: word to start off with
    :except not a dict, int, string
    :return: string: predicted text of length = text_length
    """

    try:
        n = max(ngram_models, key=int)
        V = len(ngram_models[1].keys())
        if n == 1:
            max_value = max(ngram_models.get(1).values())
            max_key = [k for k, v in ngram_models.get(1).items() if v == max_value]
            seed_word = '<s> ' + seed_word
            while text_length > len(seed_word.split()):
                seed_word = seed_word + " " + max_key[0]
            return seed_word
        if text_length == 1:
            return '<s>'
        if '<s>' not in seed_word:
            seed_word = '<s>' + " " + seed_word

        if len(seed_word.split()) == text_length:
            return seed_word
        seed_word_tokens = seed_word.split()
        max_prob = -1
        most_probable_line = ""
        if len(seed_word_tokens) == 2 and '<s>' not in seed_word and n != 2:
            return ""+generate_text(ngram_models, text_length, seed_word)
        elif len(seed_word_tokens) < n:
            for key in ngram_models.get(1):
                word = seed_word + " " + key
                word_len = len(word.split())
                count_num = ngram_models.get(word_len).get(word, 0)+1
                count_den = ngram_models.get(word_len-1, ngram_models.get(1)).get(seed_word, 0)+V
                prob = float(count_num)/count_den
                if prob > max_prob:
                    max_prob = prob
                    most_probable_line = word
            return ""+generate_text(ngram_models, text_length, most_probable_line)

        else:
            # for key in ngram_models.get(1):
            list_str_prev = seed_word_tokens[len(seed_word_tokens)-n+1:]
            str_prev = " ".join(str(x) for x in list_str_prev)
            for key in ngram_models.get(1):
                word = str_prev + " " + key
                word_len = len(word.split())
                count_num = ngram_models.get(word_len).get(word, 0) + 1
                count_den = ngram_models.get(word_len - 1).get(seed_word, 0) + V
                prob = float(count_num) / count_den
                if prob > max_prob:
                    max_prob = prob
                    most_probable_line = seed_word + " " + key
            return ""+generate_text(ngram_models, text_length, most_probable_line)
    except:
        print ("invalid data")
        return ""
