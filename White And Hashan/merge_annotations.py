import collections
import csv
import os


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


def read_annotations(q_name, q_name_dir, annotations_dict):
    for f in os.listdir(q_name_dir):
     #   print(q_name_dir)
     #   print(f)
        if (not f.endswith('.csv')):
            continue
        with open(q_name_dir + '\\' + f, 'r',  newline='') as annotated_csv:
            reader = csv.DictReader(annotated_csv)
            for row in reader:
                if not row['category']:
                    print('missing value at ' + q_name_dir + '\\' + f)
                    continue
                category = row['category'].strip()
                if 'document_url' in row:
                    url = row['document_url']
                else:
                    row['url']
                annotations_dict[q_name][f][url].append(category)


def get_annotations_mult(annotations_dict, q_name, cls_dir, div):
    for annotator in os.listdir(cls_dir):
        if annotator.endswith('.ZIP') or annotator.endswith('.zip') or annotator.endswith('.rar') or annotator.endswith('.7z'):
            continue
        annotators_dir = cls_dir + annotator + '\\'
        if div in os.listdir(annotators_dir):
            q_name_dir = annotators_dir + div +'\\' + q_name
            if os.path.exists(q_name_dir):
                read_annotations(q_name, q_name_dir, annotations_dict)


def get_annotations_two_batches(annotations_dict, q_name, cls_dir):
    for annotator  in os.listdir(cls_dir):
        if annotator.endswith('.ZIP') or annotator.endswith('.zip') or annotator.endswith('.rar') or annotator.endswith('.7z'):
            continue
        annotators_dir = cls_dir + annotator + '\\'
        q_name_dir = annotators_dir  + '\\' + q_name
        if os.path.exists(q_name_dir):
            read_annotations(q_name, q_name_dir, annotations_dict)

def get_annotations_divs(annotations_dict,w_h_dir, div_names, cls_dir, mult):
    for div in div_names:
        div_queries = os.listdir(w_h_dir + div)
        for q_name in div_queries:
            if mult:
                get_annotations_mult(annotations_dict, q_name, cls_dir, div)
            else:
                get_annotations_two_batches(annotations_dict, q_name, cls_dir)


def get_all_annotations(annotations_dict, two_batches_w_h, multiple_cls, mult_w_and_h,two_batches_cls ):
    batch_divs = ['batch_div' + str(i) for i in range(1, 34)]
    get_annotations_divs(annotations_dict, mult_w_and_h, batch_divs, multiple_cls, True)
    get_annotations_divs(annotations_dict, two_batches_w_h, ['batch1', 'batch2'],two_batches_cls, False)



def init_annotations_dict(root_dir):
    annotations = {}
    for batch in  ['batch1\\', 'batch2\\']:
        for query_dir in os.listdir(root_dir+batch):
            annotations[query_dir] = {}
            for f in os.listdir(root_dir+batch+query_dir):
                annotations[query_dir][f] = {}
                with open(root_dir + batch + query_dir + '\\' +f, 'r', encoding='utf-8', newline='') as annotated_csv:
                    reader = csv.DictReader(annotated_csv)
                    for row in reader:
                        if 'document_url' in row:
                            annotations[query_dir][f][row['document_url']] = list()
                        else:
                            annotations[query_dir][f][row['url']] = list()
    return annotations

def fill_majority_dict(annotations_dict, majority_dict):
    for query, files in annotations_dict.items():
        for f, f_content in files.items():
            for doc_url, annotations in f_content.items():
                if len(annotations) < 3:
                    continue
                count = collections.Counter(annotations)
                sorted_count = sorted(count.items(), key=lambda item: item[1], reverse=True)
                winner_count = sorted_count[0][1]
                winner_val = sorted_count[0][0]
                if winner_count <= 1:
                    continue
                if not query in majority_dict:
                    majority_dict[query] = {}
                if not f in majority_dict[query]:
                    majority_dict[query][f] = {}

                majority_dict[query][f][doc_url] = int(winner_val)
#                if len(sorted_count > 1) :
#                    runner_up  = sorted_count[1][1]


def write_merge_files(majority_dict, merge_dir):
    for q, files in majority_dict.items():
        os.mkdir(merge_dir + q)
        for f, urls in files.items():
            with open(merge_dir + q + '\\' + f, 'w', newline='') as csv_f:
                wr = csv.DictWriter(csv_f, fieldnames=['document_url','category'])
                wr.writeheader()
                for url, category in urls.items():
                    wr.writerow({'document_url':url, 'category': category})


def merge(two_batches_w_h, multiple_cls, mult_w_and_h, two_batches_cls, merge_dir):
    annotations_dict = init_annotations_dict(two_batches_w_h)
    get_all_annotations(annotations_dict, two_batches_w_h, multiple_cls, mult_w_and_h, two_batches_cls)
    majority_dict = {}
    fill_majority_dict(annotations_dict, majority_dict)

    if not os.path.exists(merge_dir):
        os.mkdir(merge_dir)
    write_merge_files(majority_dict, merge_dir)

def test():
    mult_w_and_h = 'C:\\research\\falseMedicalClaims\\White and Hassan\\to_classify\\multiple batches\\'
    two_batches_w_h = 'C:\\research\\falseMedicalClaims\\White and Hassan\\to_classify\\two batches\\'

    cls_root = 'C:\\Users\\User\\PycharmProjects\\Medical_Project\\resources\\merge_annotations_test\\'
    multiple_cls = cls_root + 'multiple batches\\'
    two_batches_cls = cls_root + 'two batches\\'
    merge_dir = 'C:\\Users\\User\\PycharmProjects\\Medical_Project\\resources\\merge_annotations_actual\\'
    merge(two_batches_w_h, multiple_cls, mult_w_and_h, two_batches_cls, merge_dir)

def main():
    two_batches_w_h = 'C:\\research\\falseMedicalClaims\\White and Hassan\\to_classify\\two batches\\'
    multiple_cls ='C:\\research\\falseMedicalClaims\\White and Hassan\\annotated\\multiple batches\\'
    mult_w_and_h = 'C:\\research\\falseMedicalClaims\\White and Hassan\\to_classify\\multiple batches\\'
    two_batches_cls = 'C:\\research\\falseMedicalClaims\\White and Hassan\\annotated\\two batches\\'
    merge_dir = 'C:\\research\\falseMedicalClaims\\White and Hassan\\merged_annotations\\'
    merge(two_batches_w_h, multiple_cls, mult_w_and_h, two_batches_cls, merge_dir)

if __name__ == '__main__':
    main()
