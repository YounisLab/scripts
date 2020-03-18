#################################### NOTES ####################################
# - ensure chromedriver is installed in the same directory as this script     #
# - ensure you have installed the selenium library                            #
# - runtime is approx. 3 minutes                                              #
# - retrieved run IDs will be stored to runs.txt                              #
###############################################################################

from selenium import webdriver

# connect to webpage
driver = webdriver.Chrome(executable_path='./chromedriver')
url = 'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE48216'
driver.get(url) 

# expand and read table containing samples
driver.find_element_by_partial_link_text('More...').click() 
table = driver.find_elements_by_tag_name('tbody') 

# empty lists for RNA sequencing samples and their corresponding url
samplesRNA = [] 
links = []

# html structure separated data into two tables, so data is extracted from both
for entry in table[17].find_elements_by_tag_name('tr'):
    if u'RNA-Seq' in entry.text:
        samplesRNA += [entry]
for entry in table[18].find_elements_by_tag_name("tr"):
    if u'RNA-Seq' in entry.text:
        samplesRNA += [entry]

# collect corresponding links for all RNA-sequenced samples 
for sample in samplesRNA:
    for link in sample.find_elements_by_tag_name('td'):
        if u'GSM' in link.text:
            links += [driver.find_element_by_link_text(link.text).get_attribute('href')]

# create file for writing the run IDs
outputFile = open('runs.txt', 'w')

# visit each url, extract corresponding SRA value and write it to file
for link in links:
    driver.get(link)
    driver.find_element_by_partial_link_text('SRX').click()
    outputFile.write(driver.find_element_by_partial_link_text('SRR').text+'\n')

outputFile.close()
