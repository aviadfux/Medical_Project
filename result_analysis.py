import csv
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


def main():
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