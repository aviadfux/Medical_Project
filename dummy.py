import requests
import sys
import csv

def main():
    url = "https://www.ncbi.nlm.nih.gov/pubmed/"
    query_text = sys.argv[1]
    query = "?term=" + sys.argv[1].replace(' ', '+')

    r = requests.get(url + query)
    r.encoding = 'utf-8'
    div_class = r.text.split("<div class=\"rprt\">")
    div_class = div_class[1:]

    results_links = []
    for object in div_class:
        num_link = object.split("from_uid=")[1].split("\"")[0]
        results_links.append(url + num_link)

    with open("query - " + query_text + ".csv", 'w', newline='') as resultFile:
        wr = csv.writer(resultFile, dialect='excel')

        for item in results_links:
            wr.writerow([item, ])

if __name__ == '__main__':
    main()