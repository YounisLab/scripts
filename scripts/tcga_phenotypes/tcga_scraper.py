# obtain list of phenotypes that we want
import requests
import json
import csv
import os
import errno
import sys

if (len(sys.argv) != 2):
    print("Incorrect Argument Format, Usage:\n python tcga_scraper.py <download folder>")
    exit()
folder = sys.argv[1]

endpoint = "https://tcga.xenahubs.net/data/"

phenotypes_body = """(; allFieldMetadata
(fn [dataset]
	(query {:select [:field.name :feature.*]
			:from [:field]
			:where [:= :dataset_id {:select [:id]
							 :from [:dataset]
							 :where [:= :name dataset]}]
			:left-join [:feature [:= :feature.field_id :field.id]]}))
"TCGA.BRCA.sampleMap/BRCA_clinicalMatrix")"""

samples_body = """(; cohortSamples
(fn [cohort limit]
    (map :value
      (query
        {:select [:%distinct.value]
         :from [:dataset]
         :join [:field [:= :dataset.id :dataset_id]
                :code [:= :field_id :field.id]]
         :limit limit
         :where [:and [:= :cohort cohort]
                      [:= :field.name "sampleID"]]})))
 "TCGA Breast Cancer (BRCA)" 50000)"""

 # make request to api for phenotypes
r = requests.post(url=endpoint, data=phenotypes_body)

# clean up result
phenotypes = [item['name'] for item in json.loads(r.text)]

# get a list of the tcga samples
r = requests.post(url=endpoint, data=samples_body)
tcga_samples = json.loads(r.content)

# set up parameters for individual phenotype requests
body1 = """(; fieldCodes
(fn [dataset fields]
	(query
	  {:select [:P.name [#sql/call [:group_concat :value :order :ordering :separator #sql/call [:chr 9]] :code]]
	   :from [[{:select [:field.id :field.name]
				:from [:field]
				:join [{:table [[[:name :varchar fields]] :T]} [:= :T.name :field.name]]
				:where [:= :dataset_id {:select [:id]
								 :from [:dataset]
								 :where [:= :name dataset]}]} :P]]
	   :left-join [:code [:= :P.id :field_id]]
	   :group-by [:P.id]}))
 "TCGA.BRCA.sampleMap/BRCA_clinicalMatrix" """

body2 = """(; datasetProbeValues
(fn [dataset samples probes]
  (let [probemap (:probemap (car (query {:select [:probemap]
                                         :from [:dataset]
                                         :where [:= :name dataset]})))
        position (if probemap
                    (xena-query {:select ["name" "position"] :from [probemap] :where [:in "name" probes]})
                    nil)]
    [position
     (fetch [{:table dataset
              :columns probes
              :samples samples}])]))

 "TCGA.BRCA.sampleMap/BRCA_clinicalMatrix" """

 # check if desired folder exists
if not os.path.exists(os.path.dirname(folder)):
    try:
        os.makedirs(os.path.dirname(folder))
    except OSError as exc: # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise

def min_fun (x):
    if x=='NaN': return 2
    else: return x

def map_fun (x):
    if x=='NaN': return None
    else: return mappings[x-start_point]

# for each phenotype create a .csv file
for phenotype in phenotypes:
    buf = '%s ["%s"])' % (body1, phenotype)
    r1 = requests.post(url=endpoint, data= buf)
    print(phenotype)
    if (json.loads(r1.content)[0]['code']):
        mappings = json.loads(r1.content)[0]['code'].split('\t')
        # sometimes there is an empty item in list
        if mappings and mappings[0] == "":
            mappings = mappings[1:]
    else:
        mappings = None
    buf = '%s%s ["%s"])' % (body2, json.dumps(tcga_samples), phenotype)
    r2 = requests.post(url=endpoint, data= buf)
    sample_values = json.loads(r2.content)[1][0]
    start_point = min(sample_values, key=min_fun)
    if mappings:
        sample_values = list(map(map_fun, sample_values))
    # replace '\' so that name is not treated as a directory
    with open(folder + phenotype.replace('/', '-') + '.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['sample', phenotype])
        for i in range(len(tcga_samples)):
            writer.writerow([tcga_samples[i], sample_values[i]])
