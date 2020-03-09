#!/usr/bin/env python

import csv
import sys
import requests
import sys
from tcga_patients import tcga_patients

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

helper = \
'''
Usage: xenabrowser.py <genes.csv> <output.csv> [gene|exon]

Fetches TCGA BRCA raw counts from the xena browser for
each gene listed in genes.csv
'''

if len(sys.argv) != 4:
  print('Incorrect number of arguments')
  print(helper)
  exit(1)

extraction_term = ''
if sys.argv[3] == 'gene':
	extraction_term = 'HiSeqV2'
elif sys.argv[3] == 'exon':
	extraction_term = 'HiSeqV2_exon'
else:
	print('Unrecognized parameter for extraction. Valid keywords are "gene" or "exon"')

queryBodyString = '''(; datasetGeneProbesValues
(fn [dataset samples genes]
	(let [probemap (:probemap (car (query {:select [:probemap]
										   :from [:dataset]
										   :where [:= :name dataset]})))
			position (xena-query {:select ["name" "position"] :from [probemap] :where [:in :any "genes" genes]})
			probes (position "name")]
	  [position
		(fetch [{:table dataset
				 :samples samples
				 :columns probes}])])) "TCGA.BRCA.sampleMap/%s" [%s] ["%s"])'''

patient_string = ",".join(map(lambda p: "\"" + p + "\"", tcga_patients))

# Setup retries
s = requests.Session()
retries = Retry(total=3, backoff_factor=1, method_whitelist=frozenset(['GET', 'POST']))
s.mount('https://', HTTPAdapter(max_retries=retries))


with open(sys.argv[1]) as genes, open(sys.argv[2], mode='w') as out_file, open("missing.txt", mode='w') as missing:
	csv_writer = csv.writer(out_file, delimiter=',')
	if sys.argv[3] == 'gene':
		csv_writer.writerow(["gene"] + tcga_patients)
	else:
		csv_writer.writerow(["gene", "exon"] + tcga_patients)

	for progress, gene in enumerate(genes.readlines(), start=1):
		gene = gene.strip()
		print("Processing gene %d: %s" % (progress, gene))
		sys.stdout.flush()
		queryBody = queryBodyString % (extraction_term, patient_string, gene)
		r1 = s.post("https://tcga.xenahubs.net/data/", data=queryBody)
		jsonresponse = r1.json()

		if len(jsonresponse[1]) == 0:
			print("Couldn't find data for %s" % gene)
			sys.stdout.flush()
			missing.write(gene + "\n")
			continue

		if sys.argv[3] == 'gene':
			csv_writer.writerow([gene] + jsonresponse[1][0])
		else:
			total_exons = len(jsonresponse[1])
			for i in range(0, total_exons):
				csv_writer.writerow([gene, i+1] + jsonresponse[1][i])

print("Extraction complete.")
