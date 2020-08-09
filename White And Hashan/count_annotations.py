import os


def find_annotators_mult(q_name, cls_dir, div):
    annotations = 0
    for annotator  in os.listdir(cls_dir):
        if annotator.endswith('.ZIP') or annotator.endswith('.zip') or annotator.endswith('.rar') or annotator.endswith('.7z'):
            continue
        annotators_dir = cls_dir + annotator + '\\'
        if div in os.listdir(annotators_dir):
            q_name_dir = annotators_dir + div +'\\' + q_name
            if os.path.exists(q_name_dir):
                annotations += 1
    return annotations

def find_annotators_two_batches(q_name, cls_dir):
    annotations = 0
    for annotator  in os.listdir(cls_dir):
        if annotator.endswith('.ZIP') or annotator.endswith('.zip') or annotator.endswith('.rar') or annotator.endswith('.7z'):
            continue
        annotators_dir = cls_dir + annotator + '\\'
        q_name_dir = annotators_dir  + '\\' + q_name
        if os.path.exists(q_name_dir):
            annotations += 1
    return annotations


def count_annotations(annotations, w_h_dir, cls_dir, div_names, mult):
    for div in div_names:
        div_queries = os.listdir(w_h_dir + div)
        for q in div_queries:
            if mult:
                annotations[q] += find_annotators_mult(q, cls_dir,div)
            else:
                annotations[q] += find_annotators_two_batches(q, cls_dir)


def main():
    mult_w_and_h = 'C:\\research\\falseMedicalClaims\\White and Hassan\\to_classify\\multiple batches\\'
    multiple_cls ='C:\\research\\falseMedicalClaims\\White and Hassan\\annotated\\multiple batches\\'
    two_batches_w_h = 'C:\\research\\falseMedicalClaims\\White and Hassan\\to_classify\\two batches\\'
    two_batches_cls = 'C:\\research\\falseMedicalClaims\\White and Hassan\\annotated\\two batches\\'

    queries = os.listdir(two_batches_w_h + 'batch1')
    queries.extend(os.listdir(two_batches_w_h + 'batch2'))
    annotations = {q: 0 for q in queries}
    batch_divs = ['batch_div' + str(i) for i in range (1,34)]
    count_annotations(annotations, mult_w_and_h, multiple_cls, batch_divs, True)
    count_annotations(annotations, two_batches_w_h, two_batches_cls, ['batch1', 'batch2'], False)
    for q, count in annotations.items():
        print(q + ',' + str(count))





if __name__ == '__main__':
    main()
