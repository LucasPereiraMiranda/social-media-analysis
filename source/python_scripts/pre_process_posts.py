#coding: utf-8 

from datetime import datetime
from datetime import timedelta
from nltk.stem.snowball import SnowballStemmer
import json,re,nltk,gzip,string,unicodedata,time


#===============================================================================
# excecao criada
#===============================================================================
class PostWithoutMessageException(Exception):
    pass

#===============================================================================
# obter tempo atual
#===============================================================================
def get_current_time():
    return '%s' % (time.strftime("%Y-%m-%d--%H-%M-%S"))

#===============================================================================
# remove urls
#===============================================================================
def remove_url(text):
    return re.sub(r"http\S+", "", text)

#===============================================================================
# remove numeros no texto
#===============================================================================
def remove_numbers(text):
    return re.sub(r'\d+','',text)

#===============================================================================
# tokeniza o texto - 'hello world' return ['hello','world']
#===============================================================================
def tokenization(text):
    return nltk.word_tokenize(text)

#===============================================================================
# converte o texto para minusculo
#===============================================================================
def convert_to_lower(text):
    return text.lower()

#===============================================================================
# obter o stemming de uma lista de palavras tokenizadas
#===============================================================================
def obtain_stemming(tokenized_pre_processed_message):
    stemmer = SnowballStemmer('portuguese')
    tokenized_stemmed_text = [stemmer.stem(word) for word in tokenized_pre_processed_message]
    return tokenized_stemmed_text

#===============================================================================
# remove todos simbolos dentro da lista string.punctuation
#===============================================================================
def remove_symbols(tokenized_pre_processed_message):
    # ponctuations less [\] because unicode patterns
    ponctuations = string.punctuation.replace('[\]','')
    new_words = []
    for word in tokenized_pre_processed_message:
        new_word = ''.join([letter for letter 
            in word if letter not in ponctuations])
        if new_word != '':
            new_words.append(new_word)
    return new_words 

#===============================================================================
# remover stop words
#===============================================================================
def replace_stop_words(tokenized_pre_processed_message):
    stop_words = [word for word in nltk.corpus.stopwords.words('portuguese')]
    processed_text = [word for word in tokenized_pre_processed_message if word not in stop_words]
    return processed_text

#===============================================================================
# substituir todos /n dentro de um texto por um espaco em branco
#===============================================================================
def replace_break_lines(text):
    return text.replace('\n', ' ')

#===============================================================================
# funcao para chamar as funcoes intermediarias do pre-processamento 
#===============================================================================
def pre_process_message(message):
    pre_processed_message = remove_url(message)
    pre_processed_message = convert_to_lower(pre_processed_message)
    pre_processed_message = replace_break_lines(pre_processed_message)
    pre_processed_message = remove_numbers(pre_processed_message)
    tokenized_pre_processed_message = tokenization(pre_processed_message)
    tokenized_pre_processed_message = replace_stop_words(tokenized_pre_processed_message)
    tokenized_pre_processed_message = remove_symbols(tokenized_pre_processed_message)
    #tokenized_pre_processed_message = obtain_stemming(tokenized_pre_processed_message)
    return tokenized_pre_processed_message

#===============================================================================
# retorna a lista com os posts do path passado como parametro
 #==============================================================================
def get_list_posts_from_path(posts_file_path):
    with gzip.open(posts_file_path) as post_file:
        post_list =  post_file.readlines()
    return post_list

#===============================================================================
# normaliza os textos removendo caracteres nao ascii
#===============================================================================
def get_unicode_normalized(text):
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf8')

def generate_list_pre_processed_posts(post_list):
    pre_processed_post_list = []
    for post in post_list:
        try:
            if not isinstance(post,dict):
                dict_post = json.loads(post)
            if not 'message' in dict_post.keys() or dict_post['message'] =='':
                raise PostWithoutMessageException('this post does not have message')
            message = get_unicode_normalized(dict_post["message"])
            dict_post["pre_processed_message"] = pre_process_message(message)
            pre_processed_post_list.append(dict_post)
        except PostWithoutMessageException as err:
            dict_post["pre_processed_message"] = ' '
            pre_processed_post_list.append(dict_post)
    return pre_processed_post_list

#===============================================================================
# converte list para str - ['hello','world'] -> 'hello world'
#===============================================================================
def join_tokenized_message(tokenized_message):
    message_str = ' '
    message_str = message_str.join(tokenized_message)
    return message_str


def write_list_in_csv_file(pre_processed_post_list,output_file):

    with open(output_file, 'wt') as file:

        file.write('created_time,id,pre_processed_message,shares,status_type,full_picture,reactions_like,reactions_haha,reactions_wow,reactions_sad,reactions_angry,reactions_love\n')
        for post in pre_processed_post_list:
            file.write('{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11}\n'
                .format(str(post['created_time']),
                        str(post['id']),
                        str(join_tokenized_message(post['pre_processed_message'])),
                        str(post['shares']['count'] if ('shares' in post) else 0),
                        str(post['status_type']),
                        str(post['full_picture'] if ('full_picture' in post) else None),
                        str(post['reactions_like']['summary']['total_count']),
                        str(post['reactions_haha']['summary']['total_count']),
                        str(post['reactions_wow']['summary']['total_count']),
                        str(post['reactions_sad']['summary']['total_count']),
                        str(post['reactions_angry']['summary']['total_count']),
                        str(post['reactions_love']['summary']['total_count']),
                )
            )

def main():

    #===============================================================================
    # coloque o caminho do diretorio social-media-analysis
    #===============================================================================
    destinaton_path = '/home/lucas/UFOP/ple_2020/analise_midias_sociais/social-media-analysis'
    data_path = '%s/data' % destinaton_path

    facebook_pages = ['bolsonaro','haddad']

    for facebook_page in facebook_pages:
        print('\n\n\n*********** Starting pre processing from %s ***********\n\n\n' % facebook_page)

        posts_file_path = '%s/%s/all_posts.json.gz' % (data_path, facebook_page)
        output_posts_file_path = '%s/all_pp_posts_%s_posts.csv' % (data_path, facebook_page)

        post_list = get_list_posts_from_path(posts_file_path)
        pre_processed_post_list = generate_list_pre_processed_posts(post_list)
        write_list_in_csv_file(pre_processed_post_list,output_posts_file_path)

    #===========================================================================
    # final logs
    #===========================================================================
    print('process finished: {0}\n'.format(str(get_current_time())))

if __name__ == "__main__":
    main()