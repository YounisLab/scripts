# TCGA_FPKM_dendrogram

Generates dendrogram image and csv file holding TCGA patients and their assigned cluster colors. 

Additional optional functionality:
- Generates csv file holding TCGA patients clustered into n clusters using dendrogram's comparison function
- Generate interactive dendrogram using Plotly library
- Generate scatter plot of 2-component PCA analysis using TCGA-FPKM data

## Installation

```
pip install -r requirements.txt
```

## Usage

```
python tcga_fpkm_dendrogram.py filename
```
