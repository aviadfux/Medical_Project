import csv
import os


def unify_results(classified_file, unclassified_file, res_file):
    with open(classified_file, encoding='utf-8', newline='') as csvfile1, open(unclassified_file,encoding='utf-8',  newline='') as csvfile2:
        cls_reader = csv.DictReader(csvfile1)
        uncls_reader = csv.DictReader(csvfile2)
        cls = {}
        uncls = {}
        for row in cls_reader:
            cls[row['document_url']] = row
#        filename = unclassified_file.split('.csv')[0] + '_unified.csv'
        with open(res_file, 'w', encoding='utf-8', newline='') as resultFile:
            fieldnames = uncls_reader.fieldnames
            wr = csv.DictWriter(resultFile, fieldnames=fieldnames)
            wr.writeheader()
            for row in uncls_reader:
                url = row['document_url']
                if url and url in cls:
                    wr.writerow(dict(cls[url]))
                else:
                    wr.writerow(row)

def main():
    cls_dir = 'C:\\research\\falseMedicalClaims\\examples\\short queries\\pubmed\\classified\\'
    uncls_dir = 'C:\\research\\falseMedicalClaims\\examples\\short queries\\pubmed\\'
    cls_filename ='benzodiazepines alcohol withdrawal.csv'
    uncls_file_name = 'benzodiazepines alcohol withdrawal2.csv'
    unify_results(cls_dir+cls_filename,uncls_dir+uncls_file_name,  'C:\\research\\falseMedicalClaims\\examples\\long queries\\pubmed\\benzodiazepines alcohol withdrawal3.csv')
    dir_name = "C:\\research\\falseMedicalClaims\\examples\\long queries\\pubmed\\"
    res_dir = "C:\\research\\falseMedicalClaims\\examples\\long queries\\pubmed\\unified_new\\"
#    for filename in os.listdir(dir_name):
#        if filename.endswith(".csv"):
#            res_filename = filename.split('.csv')[0] + '_unified.csv'
#            unified_fname = filename.split('.csv')[0] + '_unified.csv'
#            unify_results(dir_name + 'unified\\classified\\' + unified_fname, dir_name+'' + filename, res_dir+res_filename)

if __name__ == '__main__':
    main()