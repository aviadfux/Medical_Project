import csv
import os

from numpy import mean


def gen_query_stats_dict(result_file, acc_column_name, error_column_name):
    with open(result_file, 'r', encoding='utf-8', newline='') as result_file:
        result_reader = csv.DictReader(result_file)
        stats = {}
        for row in result_reader:
            stats[row['query']] = {}
            stats[row['query']]['acc'] = int(row[acc_column_name])
            stats[row['query']]['err'] = int(row[error_column_name])
    return stats


def group_stats_by_key(stats, keys):
    keys_to_stats = {}
    for query, stat in stats.items():
        key = keys[query]
        if key in keys_to_stats:
            keys_to_stats[key]['acc'].append(stat['acc'])
            keys_to_stats[key]['err'].append(stat['err'])
        else:
            keys_to_stats[key] = {'acc': [stat['acc']], 'err': [stat['err']]}
    return keys_to_stats


def gen_output_file(output_filename, keys_to_stats, key_name):
    with open(output_filename, 'w', encoding='utf-8', newline='') as out:
        fieldnames = [key_name, 'error','accuracy','size']
        writer = csv.DictWriter(out, fieldnames=fieldnames)
        writer.writeheader()
        for key, stat in keys_to_stats.items():
            assert (len(stat['acc']) == len(stat['err']))
            mean_acc = mean(stat['acc'])
            mean_err = mean(stat['err'])
            writer.writerow({key_name: str(key), 'accuracy': str(mean_acc), 'error': str(mean_err), 'size' :len(stat['acc'])})


def year_to_accuracy(query_file, result_file, output_filename, acc_column_name, error_column_name):
    stats = gen_query_stats_dict(result_file, acc_column_name, error_column_name)
    years = {}
    with open(query_file, 'r', encoding='utf-8', newline='') as query_csv:
        query_reader = csv.DictReader(query_csv)
        for row in query_reader:
            date = row['date']
            year = date.split('.')[2].strip()
            years[row['long query']] = year

    years_to_stats = group_stats_by_key(stats, years)
    gen_output_file(output_filename, years_to_stats,  'year')


def sample_size_to_accuracy(sample_size_file, result_file, output_filename, acc_column_name, error_column_name):
    stats = gen_query_stats_dict(result_file, acc_column_name, error_column_name)
    rels = {}
    with open(sample_size_file, 'r', encoding='utf-8', newline='') as query_csv:
        query_reader = csv.DictReader(query_csv)
        for row in query_reader:
            size = row['rel'] #TODO - remove from features???
            rels[row['long query']] = size

    years_to_stats = group_stats_by_key(stats, rels)
    gen_output_file(output_filename, years_to_stats,  'rel')

def count_all_papers(destination_folder):
    num_files = {}
    num_relevant = {}
    total = 0
    relevant = 0
    print('title,num')
    for sub_folder_name in os.listdir(destination_folder):
        if sub_folder_name.endswith('.csv'):
            continue
        sub_folder = destination_folder+'\\'+sub_folder_name
        num_files[sub_folder_name] = 0
        num_relevant[sub_folder_name] = 0
        for file_name in os.listdir(sub_folder):
            with open(sub_folder + '\\' + file_name, 'r', encoding='utf-8', newline='') as queries_csv:
                reader = csv.DictReader(queries_csv)
                for row in reader:
                    num_files[sub_folder_name] +=1
                    total += 1
                    if int(row['category']) > 0:
                        relevant += 1
                        num_relevant[sub_folder_name] +=1

    for q,num in num_files.items():
            print(q + ', '+ str(num))
    print ('total: ' + str(total))
    print('relevant: ' + str(relevant))
    print('extracted: ' + str(total - relevant))
    print('mean  papers in query: ' + str(mean(list(num_files.values()))))
    print('mean  relevant papers for query: '+ str(mean(list(num_relevant.values()))))


def simple_count(destination_folder):
    num_files = {}
    num_relevant = {}
    total = 0
    print('title,num')
    for sub_folder_name in os.listdir(destination_folder):
        if sub_folder_name.endswith('.csv'):
            continue
        sub_folder = destination_folder+'\\'+sub_folder_name
        num_files[sub_folder_name] = 0
        num_relevant[sub_folder_name] = 0
        for file_name in os.listdir(sub_folder):
            print(sub_folder + '\\' + file_name)
            with open(sub_folder + '\\' + file_name, 'r', encoding='utf-8', newline='') as queries_csv:

                reader = csv.DictReader(queries_csv)
                for row in reader:
                    num_files[sub_folder_name] +=1
                    total += 1

    for q,num in num_files.items():
            print(q + ', '+ str(num))
    print ('total: ' + str(total))



def main():
    simple_count('C:\\research\\falseMedicalClaims\\classifieres\\luda\\to_classify_20_sample2')
    #count_all_papers('C:\\research\\falseMedicalClaims\ECAI\examples\\classified\\all_equal_weights')
    return
    reports_folder = 'C:\\research\\falseMedicalClaims\\ECAI\\model input\\Yael\\by_group\\reports\\'
    results_filename = reports_folder + 'group_features_by_stance_citation_1_report'

    sample_size_to_accuracy(sample_size_file = 'C:\\research\\falseMedicalClaims\\ECAI\\examples\\classified\\num_rels.csv',
                          result_file = results_filename + '.csv',
                          output_filename = results_filename + '_rels_analysis' +'.csv',
                          acc_column_name='DecisionTreeClassifier_acc',
                          error_column_name='DecisionTreeClassifier_error')

#    year_to_accuracy(query_file = 'C:\\research\\falseMedicalClaims\\ECAI\\examples\\classified\\queries1_2.csv',
#                          result_file = results_filename + '.csv',
#                          output_filename = results_filename + '_years_analysis' +'.csv',
#                          acc_column_name='DecisionTreeClassifier_acc',
#                          error_column_name='DecisionTreeClassifier_error')



if __name__ == '__main__':
    main()