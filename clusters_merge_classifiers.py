import csv
import pandas

import numpy
import os

from sklearn.cluster import KMeans

from merge_classifiers import get_opinion_categories




def get_url_to_clusters(examples):
    group_features = {}
    categories = [-1,1,2,3,4,5]
    empty_tuple = ('', {('theta'+str(x)) :0.0 for x in categories})
    centroids = {x:empty_tuple for x in categories}
    for url, counted_votes in examples.items():
        sum_votes = sum(counted_votes.values())
        if sum_votes == 0:
            print(url)
            continue
        group_features[url] = {'theta'+str(i):counted_votes[i]/sum_votes for i in categories}
        group_features[url]['thetaz'] = (group_features[url]['theta5']-group_features[url]['theta1'])/6
        for i in categories:
            ti = 'theta'+str(i)
            if centroids[i][1][ti] < group_features[url][ti]:
                centroids[i] = (url, group_features[url])

    centroid_urls = set([x[0] for x in centroids.values()])
    assert (len(centroid_urls) == 6)
    centroid_features = [list(x[1].values()) for x in centroids.values()]
    centroid_arr = numpy.array(centroid_features)
    X= pandas.DataFrame.from_dict(group_features.values()).to_numpy()
    kmeans = KMeans(n_clusters=6, init=centroid_arr).fit(X)
    clusters = {0:[],1:[],2:[],3:[],4:[],5:[]}
    labels = {}
    cluster_labels = {}
    for url, features in group_features.items():
        features_arr = numpy.array([list(features.values())])
        cluster = kmeans.predict(features_arr)
        assert(len(cluster) == 1)
        int_cluster = int( cluster[0])
        clusters[int_cluster].append(features)
        labels[url] = int_cluster
    for index, cluster in clusters.items():
        tau = {x:0 for x in categories}
        for example in cluster:
            for i in categories:
                tau[i] += example['theta'+str(i)]
        sorted_tau =  sorted(tau.items(), key=lambda kv: kv[1], reverse=True)
        cluster_labels[index] = sorted_tau[0][0]
    print(cluster_labels)
    url_to_cluster = {x:cluster_labels[y] for x,y in labels.items()}
    return url_to_cluster

def count_votes(opinions):
    counted_votes = {-1:0,1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for classifier, opinion in opinions.items():
        if opinion  == -2:
            opinion = -1
        counted_votes[opinion] += 1
    return counted_votes


def get_examples(queries_file, classifier_folders):
    examples = {}
    with open(queries_file, 'r', encoding='utf-8', newline='') as queries_csv:
        queries = csv.DictReader(queries_csv)
        output = {}
        for row in queries:
            #long query folder
            query_folder_name = row['long query']
            output[query_folder_name] = {}
            opinion_folders = {x: y + '\\' +query_folder_name + '\\' for x,y in classifier_folders.items()}
            opinions = {}
            for name, folder in opinion_folders.items(): #iterate annotators
                if not os.path.exists(folder):
                    continue
                #file per query
                for queries_file_name in os.listdir(folder): #iterate files
                    if not queries_file_name.endswith('.csv'):
                        continue
                    if not queries_file_name in output[query_folder_name]:
                        output[query_folder_name][queries_file_name] = []

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
                for url, categories in f_opinions.items():
                    counted_votes = count_votes(categories)
                    examples[url] = counted_votes
                    output[query_folder_name][queries_file_name].append(url)

#                    if max(counted_votes.values()) > 1:
#                        examples[url] = counted_votes
#                        output[query_folder_name][queries_file_name].append(url)
    return examples, output


def merge_classifiers_by_clustering(queries_file, classifier_folders, output_folder):
    examples, output = get_examples(queries_file, classifier_folders)
    url_to_clusters = get_url_to_clusters(examples)
    generate_output_files(output, output_folder, url_to_clusters)


def generate_output_files(output, output_folder, url_to_clusters):
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
    for query_folder, files in output.items():
        f = output_folder+'\\'+query_folder + '\\'
        if not os.path.exists(f):
            os.mkdir(f)
            for file,urls in files.items():
                with open(f+file, 'w', encoding='utf-8', newline='') as out:
                    fieldnames = ['document_url', 'category']
                    writer = csv.DictWriter(out, fieldnames=fieldnames)
                    writer.writeheader()
                    for url in urls:
                        row = {'document_url':url,'category':url_to_clusters[url]}
                        writer.writerow(row)





def main():
    queries_file='C:\\research\\falseMedicalClaims\\IJCAI\\query files\\queries_ijcai_pos_added.csv'
    classifier_folders = {'Audrie': 'C:\\research\\falseMedicalClaims\\IJCAI\\annotators\pos_neg\\Audrie\\annotated',
                          'Nechama': 'C:\\research\\falseMedicalClaims\\IJCAI\\annotators\pos_neg\\Nechama\\annotated',
                          'Sapir': 'C:\\research\\falseMedicalClaims\\IJCAI\\annotators\pos_neg\\Sapir\\annotated',
                          'Sigal': 'C:\\research\\falseMedicalClaims\\ECAI\\examples\\classified\\Sigal\\all',
                          'Irit': 'C:\\research\\falseMedicalClaims\\ECAI\\examples\\classified\\Irit\\all',
                          'Shlomi': 'C:\\research\\falseMedicalClaims\\ECAI\\examples\\classified\\Shlomi\\to_classify_20_sample2',
                          'Chavi': 'C:\\research\\falseMedicalClaims\\ECAI\\examples\\classified\\Chavi\\sample1_2',
                          'Yael': 'C:\\research\\falseMedicalClaims\\ECAI\\examples\\classified\\Yael\\sample1_and_2\\',
                          'Sigal2': 'C:\\research\\falseMedicalClaims\\IJCAI\\annotators\\sigal\\papers',
                          'Irit2': 'C:\\research\\falseMedicalClaims\\IJCAI\\annotators\\irit\\papers'}
    output_folder ='C:\\research\\falseMedicalClaims\\IJCAI\\merged_annotations\\GTIC\\'

    merge_classifiers_by_clustering(queries_file, classifier_folders, output_folder)

if __name__ == '__main__':
    main()
