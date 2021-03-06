import csv
import os
from nltk import agreement, interval_distance
from sklearn.metrics import cohen_kappa_score

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




def plurality_old(opinions):
    counter = {1: 0, 2: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for classifier, opinion in opinions.items():
        if opinion > 0:
            counter[opinion] += 1
    sorted_stance = sorted(counter.items(), key=lambda kv: kv[1], reverse=True)
    if sorted_stance[0][0] == sorted_stance[1][0]:
        return sorted_stance[1][0]
    else:
        return sorted_stance[0][0]


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
            print(opinion_file_name)
            if 'document_url' in row:
                opinion_categories[row['document_url']] = row
            else:
                opinion_categories[row['url']] = row


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


def get_majority_exp(opinions, weights):
    counter = {1: 0, 2: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for classifier, opinion in opinions.items():
        if opinion > 0:
            counter[opinion] += weights[classifier]
    sorted_stance = sorted(counter.items(), key=lambda kv: kv[1], reverse=True)
    if sorted_stance[0][1] == 0:
        return -1
    return sorted_stance[0][0]

def get_majority_orig(opinions, weights):
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


def plurality(opinions):
    counter = {1:0,2:0,3:0,4:0,5:0}
    for classifier, opinion in opinions.items():
        if opinion > 0:
            counter[opinion] += 1
    sorted_stance = sorted(counter.items(), key=lambda kv: kv[1], reverse=True)
    if sorted_stance[0][1] == 0:
        return -1
    return sorted_stance[0][0]


def get_majority(opinions, weights):
    counter = {-1: 0, 1: 0, 2: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for classifier, opinion in opinions.items():
        opinion = -1 if opinion == -2 else opinion
        counter[opinion] += weights[classifier]
    sorted_stance = sorted(counter.items(), key=lambda kv: kv[1], reverse=True)

    if sorted_stance[0][1] == sorted_stance[1][1]:
        if sorted_stance[0][0] > sorted_stance[1][0]:
            return sorted_stance[0][0]
        else:
            return sorted_stance[1][0]

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
                      output_folder='\\ijcai')


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


def merge_google_labels(dir_name, classifiers):
    labels = {}
    for (name, file) in classifiers:
        path = dir_name + file
        with open(path, 'r', encoding='utf-8', newline='') as label_file:
            label_file_dict = csv.DictReader(label_file)
            for row in label_file_dict:
                q = row['short query']
                value = int(row['Google_value'])
                if q not in labels:
                    labels[q] = {}
                    labels[q]['short query'] = q
                    labels[q][name] = value
                    if 'query' in row:
                        labels[q]['long query'] = row['query']
                else:
                    assert name not in labels[q]
                    labels[q][name] = value
                    if 'query' in row:
                        assert(labels[q]['long query'] == row['query'])
    with open(dir_name + 'google_labels_merged.csv', 'w', encoding='utf-8', newline='') as merged:
        fieldnames = ['short query', 'long query', 'Google']
        names = [x[0] for x in classifiers]
        fieldnames.extend(names)
        merged_writer = csv.DictWriter(merged, fieldnames=fieldnames)
        merged_writer.writeheader()
        taskdata = []
        taskdata_counter = 0
        for row in labels.values():
            taskdata_counter+=1
            barak_label = row['barak']
            for name in names:
                if name not in row:
                    print ('no label for ' + name + ' for query ' + row['short query'])
                    row[name] = 0

                if barak_label == -1:
                    if (name in row) and (row[name] > 0):
                        print('Error')
                        print(name)
                        print(row['short query'])

                else:
                    rating = row[name] if row[name] >  0 else 0
                    taskdata.append((name, str(taskdata_counter), rating))
            values = [row[x] for x in names]
            values.sort()
            if values[1] == values[0]:
                row['Google'] = values[0]
            elif values[1] == values[2]:
                row['Google'] = values[2]
            else:
                row['Google'] = -10
                print('DISAGREEMENT on ' + row['short query'])
            merged_writer.writerow(row)

        ratingtask = agreement.AnnotationTask(data=taskdata, distance = interval_distance)
    print("kappa " + str(ratingtask.kappa()))
    print("fleiss " + str(ratingtask.multi_kappa()))
    print("alpha " + str(ratingtask.alpha()))
    print("scotts " + str(ratingtask.pi()))


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


def get_labels(f, fieldname):
    labels = {}
    with open(f, 'r', encoding='utf-8', newline='') as label_file:
        label_file_dict = csv.DictReader(label_file)
        for row in label_file_dict:
            q = row['short query']
            value = int(row[fieldname])
            labels[q] = 0 if value < 0 else value
    return labels

def calc_kappa(f1,f2, fieldname):
    labels1 = get_labels(f1,fieldname)
    labels2 = {}
    with open(f2, 'r', encoding='utf-8', newline='') as label_file:
        label_file_dict = csv.DictReader(label_file)
        for row in label_file_dict:
            q = row['short query']
            row_value = int(row[fieldname])
            value = 0 if row_value < 0 else row_value
            assert q in labels1
            labels2[q] = value
    labeler1 = []
    labeler2=[]
    for q in labels1.keys():
        labeler1.append(labels1[q])
        labeler2.append(labels2[q])
    print(cohen_kappa_score(labeler1, labeler2, weights='quadratic'))


def merge_classifiers_by_query_file(queries_file, classifier_folders, output_folder,  exclude_ir=False):
    weights = {x:1 for x in classifier_folders.keys()}
    with open(queries_file, 'r', encoding='utf-8', newline='') as queries_csv:
        queries = csv.DictReader(queries_csv)
        for row in queries:
            query_folder_name = row['query']
            print(row['query'])
            opinion_folders = {x: y + '\\' +query_folder_name + '\\' for x,y in classifier_folders.items()}
            opinions = {}
            for name, folder in opinion_folders.items():
                if not os.path.exists(folder):
                    continue
                for queries_file_name in os.listdir(folder):
                    if not queries_file_name.endswith('.csv'):
                        continue
                    if not queries_file_name in opinions:
                        opinions[queries_file_name] = {}
                    annotations = get_opinion_categories(folder+queries_file_name)
                    for url, row in annotations.items():
                        if not row['category']:
                            continue
                        category = int(row['category'].strip())
                        if url not in opinions[queries_file_name]:
                            opinions[queries_file_name][url] = {}
                        opinions[queries_file_name][url][name] = category
            if not opinions.items():
                print('stop')
            for f_name, f_opinions in opinions.items():
                file_content = []
                for url , categories in f_opinions.items():
                    majority_vote = get_majority(categories, weights)
                    file_content.append({'document_url': url, 'category': majority_vote})
                if not os.path.exists(output_folder + '\\' + query_folder_name):
                    os.mkdir(output_folder + '\\' + query_folder_name)
                gen_output_file(output_folder + '\\' + query_folder_name + '\\'+f_name, file_content)

def merge_all_ijcai_ecai():
    classifier_folders = {#'Audrie':'C:\\research\\falseMedicalClaims\\IJCAI\\annotators\pos\\Audrie\\annotated',
                          #'Nechama': 'C:\\research\\falseMedicalClaims\\IJCAI\\annotators\\pos\\Nechama\\annotated',
                          #'Sapir':'C:\\research\\falseMedicalClaims\\IJCAI\\annotators\\pos\\Sapir\\annotated',
                          'Sigal': 'C:\\research\\falseMedicalClaims\\ECAI\\examples\\classified\\Sigal\\all',
                          'Irit': 'C:\\research\\falseMedicalClaims\\ECAI\\examples\\classified\\Irit\\all',
                          'Shlomi': 'C:\\research\\falseMedicalClaims\\ECAI\\examples\\classified\\Shlomi\\to_classify_20_sample2',
                          'Chavi': 'C:\\research\\falseMedicalClaims\\ECAI\\examples\\classified\\Chavi\\all',
                          'Yael': 'C:\\research\\falseMedicalClaims\\ECAI\\examples\\classified\\Yael\\sample1_and_2\\',
                          #'Irit2': 'C:\\research\\falseMedicalClaims\\IJCAI\\annotators\\irit\\papers\\',
                          #'Sigal2': 'C:\\research\\falseMedicalClaims\\IJCAI\\annotators\\sigal\\papers\\'
                          }
    merge_classifiers_by_query_file(
        queries_file='C:\\research\\falseMedicalClaims\\IJCAI\\query files\\queries ecai.csv',
        classifier_folders=classifier_folders,
        output_folder='C:\\research\\falseMedicalClaims\\IJCAI\\merged_annotations\\ecai_query\\',
        exclude_ir=False)

def merge_all_ijcai():
    classifier_folders = {'Audrie':'C:\\research\\falseMedicalClaims\\IJCAI\\annotators\pos_neg\\Audrie\\annotated',
                         # 'Nechama': 'C:\\research\\falseMedicalClaims\\IJCAI\\annotators\\pos_neg\\Nechama\\annotated',
                          'Sapir':'C:\\research\\falseMedicalClaims\\IJCAI\\annotators\\pos_neg\\Sapir\\annotated',
                          'Sigal': 'C:\\research\\falseMedicalClaims\\ECAI\\examples\\classified\\Sigal\\all',
                          'Irit': 'C:\\research\\falseMedicalClaims\\ECAI\\examples\\classified\\Irit\\all',
                          'Chavi2': 'C:\\research\\falseMedicalClaims\\IJCAI\\annotators\\Chavi\\all',
                          'Shlomi': 'C:\\research\\falseMedicalClaims\\ECAI\\examples\\classified\\Shlomi\\to_classify_20_sample2',
                          'Chavi': 'C:\\research\\falseMedicalClaims\\ECAI\\examples\\classified\\Chavi\\all',
                          'Yael': 'C:\\research\\falseMedicalClaims\\ECAI\\examples\\classified\\Yael\\sample1_and_2\\',
                          'Irit2': 'C:\\research\\falseMedicalClaims\\IJCAI\\annotators\\irit\\papers\\',
                   #      'Sigal2': 'C:\\research\\falseMedicalClaims\\IJCAI\\annotators\\sigal\\papers\\',
                          'Yael2':'C:\\research\\falseMedicalClaims\IJCAI\\annotators\\Yael\\papers_is_Yael'
                          }
    merge_classifiers_by_query_file(
        queries_file='C:\\research\\falseMedicalClaims\\IJCAI\\query files\\queries only.csv',
        classifier_folders=classifier_folders,
        output_folder='C:\\research\\falseMedicalClaims\\IJCAI\\merged_annotations\\ns\\',
        exclude_ir=False)

def main():
    merge_all_ijcai()
    #merge_all()
    return
    merge_google_labels('C:\\research\\falseMedicalClaims\\IJCAI\\classification\\Google labels\\',
                        [('irit','google labels  irit.csv'),
                         ('sigal','google labels_sigal.csv'),
                         ('barak','google labels barak.csv')])
    return

    calc_kappa('C:\\research\\falseMedicalClaims\\IJCAI\\classification\\cochrane\\cochrane_no_label - irit.csv',
               'C:\\research\\falseMedicalClaims\\IJCAI\\classification\\cochrane\\cochrane_no_label_sigal.csv',
               'label')

    calc_kappa('C:\\research\\falseMedicalClaims\\IJCAI\\classification\\Google labels\\google labels  irit.csv',
               'C:\\research\\falseMedicalClaims\\IJCAI\\classification\\Google labels\\google labels_sigal.csv',
               'Google_value')


if __name__ == '__main__':
    main()