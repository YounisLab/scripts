```
usage: pearson_index.py [-h] fpkm_db rbp_list output_file

Generates pearson correlation index for a given list of RBPs.

positional arguments:
  fpkm_db      .csv file containing fpkm information for all genes across all
               patients from the TCGA study. MUST BE TAB-DELIMITED.
  rbp_list     List of rbps to calculate pearson index for.
  output_file  Path to output file. Maps rows to genes.
```
