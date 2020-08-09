import csv
import os
import random

from nltk import agreement, interval_distance, custom_distance
from numpy.matlib import rand
from sklearn.metrics import cohen_kappa_score

from py._xmlgen import raw



def get_labels(f, title_filed, label_field, value_dict):
    labels = {}
    with open(f, 'r', newline='', encoding="utf-8") as label_file:
        label_file_dict = csv.DictReader(label_file)
        for row in label_file_dict:
            q = row[title_filed].strip()
            if row[label_field]:
                value = value_dict[row[label_field].strip()]
                labels[q] = 0 if value < 0 else value
    return labels


def calc_kappa(doctor,w_and_h,disag_file, cmp_file):
    w_and_h_labels =  get_labels(w_and_h,'long query','label',{'does not help':1,'inconclusive':2,'helps':3,})
    doctor_labels = get_labels(doctor,'Title','Label',{'1':1,'2':1,'3':2,'4':3,'5':3})

    labeler1 = []
    labeler2=[]
    disag = []
    cmp = []
    for query, label in doctor_labels.items():
        w_and_h_label = w_and_h_labels[query]
        if not query in w_and_h_labels:
            print(query + ' not in w&H file!!')
            continue
        cmp.append({'query':query, 'Doctor': label, 'W&H':w_and_h_label})
        if label != w_and_h_label:
            disag.append({'query':query, 'Doctor': label, 'W&H':w_and_h_label})
        labeler1.append(label)
        labeler2.append(w_and_h_label)
    print('kappa='+str(cohen_kappa_score(labeler1, labeler2, weights='quadratic')))
    with open(disag_file, 'w', newline='') as diag_csvfile, open(cmp_file, 'w', newline='') as cmp_csvfile:
        fieldnames = ['query', 'Doctor', 'W&H']
        disag_writer = csv.DictWriter(diag_csvfile, fieldnames=fieldnames)
        disag_writer.writeheader()
        cmp_writer = csv.DictWriter(cmp_csvfile, fieldnames=fieldnames)
        cmp_writer.writeheader()
        for row in disag:
            disag_writer.writerow(row)
        for row in cmp:
            cmp_writer.writerow(row)



def main():

    calc_kappa('C:\\research\\falseMedicalClaims\\White and Hassan\\doctors annotations\\queries_ashkenazi.csv',
               'C:\\research\\falseMedicalClaims\\White and Hassan\\truth_detailed_comma.csv',
               'C:\\research\\falseMedicalClaims\\White and Hassan\\doctors annotations\\ashkenazi_disag.csv',
               'C:\\research\\falseMedicalClaims\\White and Hassan\\doctors annotations\\ashkenazi_cmp.csv')


if __name__ == '__main__':
    main()
