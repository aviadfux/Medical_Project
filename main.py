import sys
import csv
from selenium import webdriver

URL = "https://www.ncbi.nlm.nih.gov/pubmed/"
global If_need_best_match_button

def create_query_csv(query, results):
    filter = sys.argv[2]

    with open("query - " + query + "_filter - " + filter + ".csv", 'w', newline='') as resultFile:
        wr = csv.writer(resultFile, dialect='excel')

        for item in results:
            wr.writerow([item, ])

def query_from_server(raw_query, driver):
    query = "?term=" + raw_query.replace(' ', '+')

    driver.get(URL + query)

    global If_need_best_match_button
    if If_need_best_match_button:
        driver.find_element_by_link_text('Best match').click()
        If_need_best_match_button = False

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
    return webdriver.Chrome(options=options, executable_path=r'C:/chromedriver_win32/chromedriver')

def main():
    with open(sys.argv[1], 'r') as queries_file:
        content = queries_file.readlines()
        # you may also want to remove whitespace characters like `\n` at the end of each line
        queries = [x.strip() for x in content]

    global If_need_best_match_button
    if sys.argv[2] == 'Best match':
        If_need_best_match_button = True
    else:
        If_need_best_match_button = False

    chrome = open_chrome_driver()

    limit_results = int(sys.argv[3])
    for num, query in enumerate(queries):
        if num >= limit_results: break
        results = query_from_server(query, chrome)
        create_query_csv(query, results)

if __name__ == '__main__':
    main()