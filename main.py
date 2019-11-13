import ast
import os
import sys
import csv
import time
from distutils.util import strtobool

import scholarly as scholarly
from metapub import PubMedFetcher

#import stopwords as stopwords
from selenium import webdriver

URL = "https://www.ncbi.nlm.nih.gov/pubmed/"
exclude_phrases = ["Dietary","related interventions", "Interventions", "improving", "supplementation", "supplements",]
my_stop_words = ["and\/or", "as","a","an", "and", "or", "do", "help", "does", "(", ")", "due", "to", "prevent", "treat", "preventing", "prevention", "treatment", "treating",
                  "and/or"]


def remove_stop_words(query):
    #stop_words = stopwords.words('english')
    query = query.replace('(','')
    query = query.replace(')', '')
    tokenized_words = query.lower().split(' ')
    tokens = [word for word in tokenized_words if word not in my_stop_words]
    return ' '.join(tokens)

def num_of_results_per_page(driver, num_results):
    time.sleep(3)
    #Click on 'Per page'
    driver.find_element_by_xpath("// *[ @ id = \"result_action_bar\"] / ul / li[3]").click()

    options = [5,10,20,50,100,200]
    differ = []
    [differ.append(option - num_results) for option in options if (option - num_results) >= 0]

    #20 is the defult value of num results
    if num_results + differ[0] == 20: return
    li_num = options.index(num_results + differ[0]) + 1
    time.sleep(3)
    # Click on the desired num results on page
    driver.find_element_by_xpath("// *[ @ id = \"display_settings_menu_ps\"] / fieldset / ul / li[%s] / label" % li_num).click()

def create_query_csv(filename, results, suffix, destination_folder,  to_exclude = None):

    to_print = []
    if to_exclude:
        for result in results:
            if not result in to_exclude:
                to_print.append(result)
    else:
        to_print = results
    #filename = destination_folder + '\\' + query[0] + "_" + sort + ".csv"
    filename = destination_folder + '\\' + filename + "_"+ suffix + ".csv"
    with open(filename , 'w', newline='') as resultFile:
        wr = csv.writer(resultFile, dialect='excel')
        wr.writerow(["document_url", "category"])
   #     wr.writerow(["document_url", "category", "numeric"])
        for item in to_print:
            wr.writerow([item, ])

def query_from_google():
    #query = "?term=" + raw_query.replace(' ', '+')

    driver = open_chrome_driver()
    driver.get('https://www.google.com/search?q="Antioxidants+for+female+subfertility"+pubmed')
    #x= driver.find_element_by_class_name('g')
    links = driver.find_elements_by_partial_link_text('ncbi')
    for link in links:
        print(link.get_attribute("href"))


def query_from_server(parsed_query, end_year, filter_method):

    #parsed_query = join_query(raw_query)
    #query = "?term=" + parsed_query.replace(' ', '+')
    query = "?term=" + parsed_query.replace(' ', '+')

    driver = open_chrome_driver()
    driver.get(URL + query)

    #num_of_results_per_page(driver, limit_results)

    #driver.find_element_by_link_text('10 years').click()
#    driver.find_element_by_link_text('Best match').click()
    #best matcch
    #driver.find_element_by_xpath('// *[ @ id = "ui-portlet_content-4"] / ul / li[1]').click()

    st_year = str(int(end_year) - 15)
    driver.find_element_by_link_text('Custom range...').click()
    driver.find_element_by_id("facet_date_st_yeards1").send_keys(st_year)
    driver.find_element_by_id("facet_date_end_yeards1").send_keys(end_year)
    driver.find_element_by_xpath('//*[@id="facet_date_range_applyds1"]/span').click()


    #
    #if press_button:
    #print("sleep 10")
    time.sleep(5)
    driver.find_element_by_link_text('Abstract').click()
    time.sleep(5)
    driver.find_element_by_link_text('Best match').click()
    time.sleep(5)
    if filter_method == 'clinical':
        driver.find_element_by_link_text('Clinical Trial').click()
        time.sleep(5)
    elif filter_method == 'rev':
        driver.find_element_by_link_text('Review').click()
        time.sleep(5)


    page_source = driver.page_source

    div_class = page_source.split("<div class=\"rprt\">")
    div_class = div_class[1:]
    results_links = []
    for object in div_class:
        num_link = object.split("from_uid=")[1].split("\"")[0]
        results_links.append(URL + num_link)
        if len(results_links) == 10:
            driver.close()
            return results_links
    driver.close()
    return results_links

def open_chrome_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--test-type")
    return webdriver.Chrome(options=options, executable_path=r'chromedriver')

def filter_results(results, words_in_tilte, limit):
    fetch = PubMedFetcher(email='anat.hashavit@gmail.com')
    filtered_results = []
    counter = 0
    for paper in results:
        pmid = paper.split('/')[-1].split('\n')[0]
        article = fetch.article_by_pmid(pmid)
        for words in words_in_tilte:
            include = False
            for word in words:
                if word.strip().lower() in article.title.lower():
                    include = True
                    continue
            if not include:
                break
        if include:
            filtered_results.append(paper)
            counter +=1
        if counter == limit:
            return filtered_results

    return filtered_results


def try_to_read_from_server(r, query, end_year, filter_method):
    try:
        return query_from_server(query, end_year, filter_method)
    except Exception as inst:
        print(type(inst))
        print(inst.args)
        print(inst)
        print('bad query at row ' + str(r))
        print(query)
        return []
        #raise (inst)


def get_all_papers(destination_folder):
    num_files = {}
    total = 0
    print('title,num')
    for sub_folder_name in os.listdir(destination_folder):
        if sub_folder_name.endswith('.csv'):
            continue
        sub_folder = destination_folder+'\\'+sub_folder_name
        num_files[sub_folder_name] = 0
        for file_name in os.listdir(sub_folder):
            with open(sub_folder + '\\' + file_name, 'r', encoding='utf-8', newline='') as queries_csv:
                reader = csv.DictReader(queries_csv)
                for row in reader:
                    #all.append(row)
                    num_files[sub_folder_name] +=1
                    total+=1
    for q,num in num_files.items():
        print(q + ', '+ str(num))
    print ('total: ' + str(total))


def main():
    destination_folder = 'C:\\research\\falseMedicalClaims\\ECAI\\examples\\unclassified\\to_classify_20_sample2\\'
    #destination_folder = 'C:\\research\\falseMedicalClaims\\examples\\short queries\\pubmed\\CAM\\x_for_y\\to_classify_20\\'
    #queries_file_name = 'C:\\research\\falseMedicalClaims\\examples\\query files\\x_for_y_queries_sample.csv'
    queries_file_name = 'C:\\research\\falseMedicalClaims\\examples\\query files\\x_for_y_queries_sample2.csv'

    get_all_papers(destination_folder)
    return
    #query_from_google()
    #search_query = scholarly.search_keyword('antioxidants+female+fertility+&hl=en&as_sdt=0%2C5&as_ylo=2007&as_yhi=2017')
    #search_query = scholarly.search_keyword('antioxidants female fertility')
    #print(next(search_query))
    #default vals:
    limit_results = 25
    best_match = True


    #queries_file_name = 'C:\\research\\falseMedicalClaims\\examples\\query files\\single.csv'

#    for i in range(1, len(sys.argv)):
#        key_val_pair = sys.argv[i].split('=')
#        key = key_val_pair[0]
#        value = key_val_pair[1]
#
#        if key == '-f':
#            queries_file_name = value
#        if key == '-b':
#            best_match = strtobool(value)
#        if key == '-l':
#            limit_results = int(value)
#        if key == '-d':
#            destination_folder = value
    queries = []
    r = 0

    with open(queries_file_name, 'r', encoding='utf-8', newline='') as queries_csv:
        reader = csv.DictReader(queries_csv)
        for row in reader:
            queries.append(row)

    press_button = best_match
    all_qs = []
    for i in range(0,len(queries)):
        r += 1
        parsed_query = queries[i]['short query']
        #parsed_query = remove_stop_words(queries[i]['short query'])
        #print(parsed_query)
        #queries[i]['short query'] = parsed_query
        folder_name = queries[i]['long query']
        query_dir = destination_folder + folder_name
        if os.path.exists(query_dir):
            continue
        date =  queries[i]['date']
        review_year = date.split('.')[2].strip()
        clinical = try_to_read_from_server(r, parsed_query,review_year, 'clinical')
        rev = try_to_read_from_server(r, parsed_query, review_year, 'rev')
        all_qs.extend(clinical)
        all_qs.extend(rev)
        all = []
        if len(all_qs) < 20:
            all = try_to_read_from_server(r, parsed_query, review_year, 'all')
            all_qs.extend(all)
        #filtered_results = filter_results(results, query[1], limit_results)

        os.mkdir(query_dir)
        create_query_csv(parsed_query, clinical, "clinical", query_dir)
        create_query_csv(parsed_query, rev, "rev", query_dir)
        exclude = rev + clinical
        create_query_csv(parsed_query, all, "rest", query_dir, exclude)

        press_button = False

    with open(destination_folder +'queries.csv', 'w', encoding='utf-8', newline='') as out:
        fieldnames = queries[0].keys()
        writer = csv.DictWriter(out, fieldnames=fieldnames)
        writer.writeheader()
        for q in queries:
            writer.writerow(q)

    create_query_csv('all', all_qs, "all", destination_folder)


if __name__ == '__main__':
    main()