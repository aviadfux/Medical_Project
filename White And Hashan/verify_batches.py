import os
import csv


def check_all_files_classified(batch_folder, cls_folder):
    dist = {x:0 for x in [0,1,2,3,4,5]}
    for sub_folder_name in os.listdir(batch_folder):
        sub_folder = batch_folder+'\\'+sub_folder_name
        cls_sub_folder = cls_folder+'\\'+sub_folder_name
        if not (os.path.exists(cls_sub_folder)):
            print('Missing folder: ' + sub_folder_name)
            continue
        for file_name in os.listdir(sub_folder):
            cls_file_path = cls_sub_folder +'\\' + file_name
            if not (os.path.exists(cls_file_path)):
                print('Missing file: ' + file_name)
                continue
            with open(sub_folder + '\\' + file_name, 'r', newline='') as papers_csv,\
                    open(cls_file_path, 'r', newline='') as classified_csv:
                reader = csv.DictReader(papers_csv)
                cls_resder  = csv.DictReader(classified_csv)
                urls = []
                cls_urls = {}
                for row in reader:
                    urls.append(row['document_url'])
                for row in cls_resder:
                    try:
                        category  = int(row['category'])
                    except:
                        category =''

                    cls_urls[row['document_url']] = category
                    if category not in dist:
                        print('missing values for file '+ file_name +' and url ' + row['document_url'])
                        continue
                    assert (category in dist)
                    dist[category] += 1
                cls_urls_keys = list(cls_urls.keys())
                if not  (len(cls_urls_keys) == len(urls)):
                    print('missing urls for file ' +  file_name)
                    continue

                for url in urls:
                    if url not in cls_urls_keys:
                        print (url + ' not original file:' +  file_name)
                    assert (url in cls_urls_keys)
    print(dist)
    sum_dist = sum(dist.values())
    dist_normed = {x:y/sum_dist for x,y in dist.items()}
    print(dist_normed)
    print(sum_dist)
    return sum_dist


def verify_batches(from_batch, to_batch, w_and_h, cls):
    num_files = 0
    for i in range(from_batch,to_batch+1):
        print('batch' +str(i))
        num_files += check_all_files_classified( batch_folder=w_and_h + 'batch_div'+str(i)+'\\',
            cls_folder=cls + 'batch_div'+str(i)+'\\')

    print('total num files = ' + str(num_files))

def verify_all_batches(w_and_h, cls):
    num_files = 0
    batch_divs = os.listdir(cls)
    for batch in batch_divs:
        if not 'batch_div' in batch:
            continue
        print(batch)
        num_files += check_all_files_classified( batch_folder=w_and_h + batch+'\\',cls_folder= cls + batch+'\\')
    print('total num files = ' + str(num_files))

def main():
    verify_all_batches(w_and_h='C:\\research\\falseMedicalClaims\\White and Hassan\\to_classify\\multiple batches\\',
                   cls='C:\\research\\falseMedicalClaims\\White and Hassan\\annotated\\multiple batches\\masha\\')

 #   verify_batches(8,12,w_and_h='C:\\research\\falseMedicalClaims\\White and Hassan\\to_classify\\multiple batches\\',
  #                 cls='C:\\research\\falseMedicalClaims\\White and Hassan\\annotated\\multiple batches\\masha\\')



if __name__ == '__main__':
    main()
