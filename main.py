import sys
import csv
from distutils.util import strtobool

#import stopwords as stopwords
from selenium import webdriver

URL = "https://www.ncbi.nlm.nih.gov/pubmed/"
my_stop_words = ["do", "help", "treat", "does"]

def remove_stop_words(query):
    #stop_words = stopwords.words('english')
    tokenized_words = query.lower().split(' ')
    tokens = [word for word in tokenized_words if word not in my_stop_words]
    return ' '.join(tokens)

def create_query_csv(query, results, bestMatch, destination_folder):
    if bestMatch:
        sort = "bestMatch"
    else:
        sort = "Recent"
    filename = destination_folder + '\\' + query + "_" + sort + ".csv"
    with open(filename , 'w', newline='') as resultFile:
        wr = csv.writer(resultFile, dialect='excel')
        wr.writerow(["document_url", ])
        for item in results:
            wr.writerow([item, ])

def query_from_server(raw_query, driver, press_button):
    parsed_quey = remove_stop_words(raw_query)
    query = "?term=" + parsed_quey.replace(' ', '+')

    driver.get(URL + query)

    if press_button:
        driver.find_element_by_link_text('Best match').click()

    page_source = driver.page_source

    div_class = page_source.split("<div class=\"rprt\">")
    div_class = div_class[1:]

    results_links = []
    for object in div_class:
        num_link = object.split("from_uid=")[1].split("\"")[0]
        results_links.append(URL + num_link)

    return results_links

def open_chrome_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--test-type")
    return webdriver.Chrome(options=options, executable_path=r'C:/Users/User/PycharmProjects/Medical_Project/chromedriver')

def main():
    #default vals:
    limit_results = 100
    best_match = False

    for i in range(1, len(sys.argv)):
        key_val_pair = sys.argv[i].split('=')
        key = key_val_pair[0]
        value = key_val_pair[1]

        if key == '-f':
            queries_file_name = value
        if key == '-b':
            best_match = strtobool(value)
        if key == '-l':
            limit_results = int(value)
        if key == '-d':
            destination_folder = value

    with open(queries_file_name, 'r') as queries_file:
        content = queries_file.readlines()
        # you may also want to remove whitespace characters like `\n` at the end of each line
        queries = [x.strip() for x in content]

    chrome = open_chrome_driver()

    press_button = best_match
    for num, query in enumerate(queries):
       # print(query)
        if num >= limit_results : break
        results = query_from_server(query, chrome, press_button)
        create_query_csv(query, results, best_match, destination_folder)
        press_button = False

if __name__ == '__main__':
    main()