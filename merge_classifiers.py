import csv
import os

from py._xmlgen import raw


def merge_3_classifiers(classifiers_folder, first_opinion_subfolder, second_opinion_subfolder, third_opinions_subfolder, output_folder):
    all_folder = classifiers_folder+ output_folder
    if not os.path.isdir(all_folder):
        os.mkdir(all_folder)
    no_majority = []
    third_opinion = []
    for query_folder_name in os.listdir(classifiers_folder + first_opinion_subfolder):
        if query_folder_name.endswith('.csv'):
            continue
        first_opinion_query_folder = classifiers_folder + first_opinion_subfolder+'\\'+query_folder_name +'\\'
        second_opinion_query_folder = classifiers_folder + second_opinion_subfolder+'\\'+query_folder_name + '\\'
        if not os.path.isdir(all_folder + query_folder_name):
            os.mkdir(all_folder + query_folder_name)
        for queries_file_name in os.listdir(first_opinion_query_folder):
            first_opinion_categories = get_opinion_categories(first_opinion_query_folder + queries_file_name)
            second_opinion_categories = get_opinion_categories(second_opinion_query_folder + queries_file_name)
            assert (len(first_opinion_categories.keys()) == len(second_opinion_categories.keys()))
            file_content = []
            for url, row in first_opinion_categories.items():
                first_opinion_category = int(row['category'].strip())
                first_opinion_category = first_opinion_category if first_opinion_category!= -2 else -1
                second_opinion_category = int(second_opinion_categories[url]['category'].strip())
                second_opinion_category = second_opinion_category if second_opinion_category != -2 else -1
                if first_opinion_category == second_opinion_category \
                        or (first_opinion_category < 0 and second_opinion_category < 0):
                    file_content.append({'document_url': url, 'category': first_opinion_category})
                else:
                    third_opinion_category = get_third_opinion(classifiers_folder, [third_opinions_subfolder],
                                                               query_folder_name, queries_file_name, url)
                    final_category = get_majority_vote(first_opinion_category, second_opinion_category,
                                                       third_opinion_category)
                    entry = {'query': queries_file_name, 'document_url': url,
                             'first_opinion': first_opinion_category,
                             'second_opinion': second_opinion_category,
                             'third_opinion': third_opinion_category}
                    if '' in row:
                        entry['comment1'] = row['']
                    if '' in second_opinion_categories[url]:
                        entry['comment2'] = second_opinion_categories[url]['']
                    if int(final_category) < 0:
                        no_majority.append(entry)
                    else:
                        third_opinion.append(entry)
                        file_content.append({'document_url': url, 'category': final_category})

            gen_output_file(all_folder + query_folder_name + '\\'+ queries_file_name, file_content)
    with open(all_folder + '_no_agreement.csv', 'w', encoding='utf-8',newline='') as no_agg_csv, \
            open(all_folder + '_all.csv', 'w', encoding='utf-8', newline='') as all_csv:
        fieldnames = ['query', 'document_url','first_opinion', 'second_opinion', 'third_opinion','comment1','comment2']
        no_agg_writer = csv.DictWriter(no_agg_csv, fieldnames=fieldnames)
        all_writer = csv.DictWriter(all_csv, fieldnames=fieldnames)
        no_agg_writer.writeheader()
        all_writer.writeheader()
        for row in no_majority:
            no_agg_writer.writerow(row)
        for row in third_opinion:
            all_writer.writerow(row)


def yael_chen():
    gen_disagreement_file('C:\\research\\falseMedicalClaims\\ECAI\\examples\\classified\\Yael\\to_classify_20_sample2_2_YAEL',
                          'C:\\research\\falseMedicalClaims\\ECAI\\examples\\classified\\Chen\\to_classify_20_sample2_2',
                          'Yael',
                          'Chen',
                          'C:\\research\\falseMedicalClaims\\ECAI\\examples\\classified\\diff_yael_chen_sample_2_2\\')


def yael_sigal():
    gen_disagreement_file(
        'C:\\research\\falseMedicalClaims\\ECAI\\examples\\classified\\Yael\\all',
        'C:\\research\\falseMedicalClaims\\ECAI\\examples\\classified\\Sigal\\sample2',
        'Yael',
        'Sigal',
        'C:\\research\\falseMedicalClaims\\ECAI\\examples\\classified\\diff_yael_sigal_sample2\\')


def gen_disagreement_file(first_opinion_folder, second_opinion_folder, first_cls_name,second_cls_name, output_folder):
    all_disagreements = []
    for query_folder_name in os.listdir(first_opinion_folder):
        if query_folder_name.endswith('.csv'):
            continue
        first_opinion_query_folder = first_opinion_folder+'\\'+query_folder_name +'\\'
        second_opinion_query_folder = second_opinion_folder+'\\'+query_folder_name + '\\'
        if not os.path.isdir(second_opinion_query_folder):
            continue

        for queries_file_name in os.listdir(first_opinion_query_folder):
            with open(first_opinion_query_folder + queries_file_name, 'r', encoding='utf-8', newline='') as first_opinion, \
                    open(second_opinion_query_folder + queries_file_name, 'r', encoding='utf-8', newline='') as second_opinion:
                first_opinion_categories = {}
                second_opinion_categories = {}
                first_opinion_reader = csv.DictReader(first_opinion)
                second_opinion_reader = csv.DictReader(second_opinion)
                for row in first_opinion_reader:
                    first_opinion_categories[row['document_url']] = row
                for row in second_opinion_reader:
                    second_opinion_categories[row['document_url']] = row
                assert (len(first_opinion_categories.keys()) == len(second_opinion_categories.keys()))
                disagreement_file_content = []
                for url, row in first_opinion_categories.items():
                    first_opinion_category = int(row['category'].strip())
                    second_opinion_category = int(second_opinion_categories[url]['category'].strip())
                    if first_opinion_category == second_opinion_category or (first_opinion_category < 0 and second_opinion_category < 0):
                        continue
                    disagreement_file_content.append(url)
                    all_disagreements_entry = ({'url':url, first_cls_name:first_opinion_category,second_cls_name:second_opinion_category})
                    if '' in row:
                        all_disagreements_entry['comment1'] = row['']
                    if '' in second_opinion_categories[url]:
                        all_disagreements_entry['comment2'] = second_opinion_categories[url]['']
                    all_disagreements.append(all_disagreements_entry)

                if not disagreement_file_content:
                    continue
                if not os.path.isdir(output_folder + query_folder_name):
                    os.mkdir(output_folder + query_folder_name)
                with open(output_folder + query_folder_name + '\\'+ queries_file_name, 'w', encoding='utf-8', newline='') as out:
                    fieldnames = ['url', 'category', 'comment']
                    writer = csv.DictWriter(out, fieldnames=fieldnames)
                    writer.writeheader()
                    for url in disagreement_file_content:
                        writer.writerow({'url':url})

    with open(output_folder + 'all.csv', 'w', encoding='utf-8',newline='') as all:
        fieldnames = ['url', first_cls_name, second_cls_name,'comment1','comment2']
        writer = csv.DictWriter(all, fieldnames=fieldnames)
        writer.writeheader()
        for q in all_disagreements:
            writer.writerow(q)


def get_third_opinion(classifiers_folder, third_opinions_subfolders, query_folder_name, queries_file_name, url):
    for subfolder in third_opinions_subfolders:
        third_opinion_query_folder = classifiers_folder + subfolder + '\\' + query_folder_name + '\\'
#        if not os.path.isdir(third_opinion_query_folder):
#            continue #TODO remove
        with open(third_opinion_query_folder + queries_file_name, 'r', encoding='utf-8', newline='') as third_opinion:
            third_opinion_reader = csv.DictReader(third_opinion)
            for row in third_opinion_reader:
                row_url = row['url']
                if row_url.strip() == url.strip():
                    try:
                        return int(row['category'].strip())
                    except ValueError:
                        print(third_opinion_query_folder + queries_file_name + ',' + url)
                        return None

    return None


#def get_all_opinions()
def get_majority_vote_from_all(opinions):
    counter = {1:0,2:0,2:0,4:0,4:0, -1:0}
    for opinion in opinions:
        int_opinion = int(opinion)
        if int_opinion == -2:
            int_opinion = -1 #-1 and -2 both mean to exclude
        counter[int_opinion] +=1
    sorted_opinions = sorted(opinion.items(), key=lambda kv: kv[1], reverse=True)
    if sorted_opinions[0] == sorted_opinions[1]:
      raise Exception
    return  sorted_opinions[0]


def get_majority_vote(first_opinion, second_opinion, third_opinion):
    if first_opinion == third_opinion:
        return first_opinion
    elif second_opinion == third_opinion:
        return second_opinion
    else:
        return -1


def get_opinion_categories(opinion_file_name):
    opinion_categories = {}
    with open(opinion_file_name, 'r', encoding='utf-8', newline='') as opinion_csv:
        opinion_reader = csv.DictReader(opinion_csv)
        for row in opinion_reader:
            opinion_categories[row['document_url']] = row
    return opinion_categories


def gen_output_file(filename, file_content):
    with open(filename, 'w', encoding='utf-8', newline='') as out:
        fieldnames = ['document_url', 'category']
        writer = csv.DictWriter(out, fieldnames=fieldnames)
        writer.writeheader()
        for row in file_content:
            writer.writerow(row)


def get_opinions(opinion_folders, queries_file_name):
    opinions_categories = {x:{} for x in opinion_folders.keys()}
    for classifier, folder in opinion_folders.items():
        filename = folder + queries_file_name
        if not os.path.isdir(folder) or not os.path.isfile(filename):
            continue
        with open(folder + queries_file_name, 'r', encoding='utf-8', newline='') as opinion_csv:
            opinion_reader = csv.DictReader(opinion_csv)
            for row in opinion_reader:
                if 'document_url' in row:
                    opinions_categories[classifier][row['document_url']] = row
                else:
                    opinions_categories[classifier][row['url']] = row
    return opinions_categories


def get_all_opinions(url, classifications):
    opinions = {}
    for classifier, queries in classifications.items():
        if not url in queries or not queries[url]['category']:
            continue
        raw_opinion = int(queries[url]['category'].strip())
        opinion = -1 if raw_opinion == -2 else raw_opinion
        opinions[classifier] = opinion
    return opinions

def get_majority(opinions, weights):
    counter = {-1:0,1:0,2:0,2:0,3:0,4:0,5:0}
    for classifier, opinion in opinions.items():
        opinion = -1 if opinion == -2 else opinion
        counter[opinion] +=weights[classifier]
    sorted_stance = sorted(counter.items(), key=lambda kv: kv[1], reverse=True)
    if sorted_stance[0][1] == sorted_stance[1][1]:
         if sorted_stance[0][0]> sorted_stance[1][0]:
             return sorted_stance[0][0]
         else:
             return sorted_stance[1][0]
        #opinion_yael = int(opinions['Yael'])
        #opinion_yael = -1 if opinion_yael ==-2 else opinion_yael
        #if opinion_yael != sorted_stance[0][0] and opinion_yael != sorted_stance[1][0]:
        #    print('YEAL MINOROTY')
        #    exit(1)
        #return opinion_yael

    return sorted_stance[0][0]


def merge_classifiers(primary_labler, classifier_folders, primary_folder, secondary_folders, weights, output_folder):
    all_folder = classifier_folders + output_folder + '\\'
    if not os.path.isdir(all_folder):
        os.mkdir(all_folder)
    for query_folder_name in os.listdir(classifier_folders + primary_folder):
        if query_folder_name.endswith('.csv'):
            continue
        query_primary_full_path = classifier_folders + primary_folder + query_folder_name
        opinion_folders = {x: classifier_folders + y  +'\\'+query_folder_name + '\\' for x,y in secondary_folders.items()}
        if not os.path.isdir(all_folder + query_folder_name):
            os.mkdir(all_folder + query_folder_name)
        for queries_file_name in os.listdir(query_primary_full_path):
            first_opinion_categories = get_opinion_categories(query_primary_full_path + '\\' + queries_file_name)
            other_classifications = get_opinions(opinion_folders=opinion_folders, queries_file_name=queries_file_name)
            file_content = []
            for url, row in first_opinion_categories.items():
                first_opinion_category = int(row['category'].strip())
                opinions = get_all_opinions(url, other_classifications)
                opinions[primary_labler] = first_opinion_category
                assert('Sigal' in opinions and 'Yael' in opinions)
                majority_vote = get_majority(opinions, weights)
                file_content.append({'document_url': url, 'category': majority_vote})
            gen_output_file(all_folder +  query_folder_name + '\\' + queries_file_name, file_content)

def merge_all():
    weights = {'Yael': 1,'Sigal':1, 'Irit':1, 'Luda':1, 'Shlomi':1, 'Chavi':1}
    secondary_folders  = {'Sigal':'Sigal\\all',
                          'Irit':'Irit\\all',
                          'Luda':'Luda\\to_classify_20_sample2  ',
                          'Shlomi':'Shlomi\\to_classify_20_sample2',
                       #   'Chen':'Chen\\to_classify_20_sample2_2',
                          'Chavi':'Chavi\\all'}
    merge_classifiers(primary_labler='Yael',
                      classifier_folders='C:\\research\\falseMedicalClaims\\ECAI\\examples\\classified\\',
                      primary_folder='Yael\\sample1_and_2\\',
                      secondary_folders=secondary_folders,
                      weights=weights,
                      output_folder='\\all')


def  shlomi_tie_breaker():
    weights = {'Yael': 1,'Sigal':1, 'Irit':1, 'Luda':0.5, 'Shlomi':0.5, 'Chavi':1}
    secondary_folders  = {'Sigal':'Sigal\\all',
                          'Irit':'Irit\\all',
                          'Luda':'Luda\\to_classify_20_sample2  ',
                          'Shlomi':'Shlomi\\to_classify_20_sample2',
                          'Chavi':'Chavi\\sample1_2'}
    merge_classifiers(primary_labler='Yael',
                      classifier_folders='C:\\research\\falseMedicalClaims\\ECAI\\examples\\classified\\',
                      primary_folder='Yael\\sample1_and_2\\',
                      secondary_folders=secondary_folders,
                      weights=weights,
                      output_folder='sample_1_2_all_shlomi_tie_breaker')


def only_strong_classifiers():
    weights = {'Yael': 1,'Sigal':0.75, 'Irit':0.75, 'Chavi':0.75}
    secondary_folders  = {'Sigal':'Sigal\\all',
                          'Irit':'Irit\\all',
                          'Chavi':'Chavi\\sample1_2'}
    merge_classifiers(primary_labler='Yael',
                      classifier_folders='C:\\research\\falseMedicalClaims\\ECAI\\examples\\classified\\',
                      primary_folder='Yael\\sample1_and_2\\',
                      secondary_folders=secondary_folders,
                      weights=weights,
                      output_folder='sample_1_2_only_strong_classifiers')

def old():
    weights = {'Yael': 1.5,'Sigal':1, 'Irit':1, 'Luda':0.75, 'Shlomi':0.75, 'Chavi':1.3}
    secondary_folders  = {'Sigal':'Sigal\\all',
                          'Irit':'Irit\\all',
                          'Luda':'Luda\\to_classify_20_sample2  ',
                          'Shlomi':'Shlomi\\to_classify_20_sample2',
                          'Chavi':'Chavi\\sample1_2'}
    merge_classifiers(primary_labler='Yael',
                      classifier_folders='C:\\research\\falseMedicalClaims\\ECAI\\examples\\classified\\',
                      primary_folder='Yael\\sample1_and_2\\',
                      secondary_folders=secondary_folders,
                      weights=weights,
                      output_folder='sample_1_2_all')


def main():
    merge_all()


if __name__ == '__main__':
    main()
