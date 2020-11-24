# TCGA_FPKM_dendrogram

Generates dendrogram image and csv file holding TCGA patients and their assigned cluster colors.

Additional optional functionality:
- Generates csv file holding TCGA patients clustered into n clusters using dendrogram's comparison function
- Generate interactive dendrogram using Plotly library
- Generate scatter plot of 2-component PCA analysis using TCGA-FPKM data

## Installation

`virtualenv` is a way to isolate software dependencies for python scripts.

First install `virtualenv`:

```bash
pip3 install virtualenv
```

Then setup and activate the virtualenv:
```bash
cd tcga_fpkm_dendogram
python3 -m venv env
source env/bin/activate
```

Then install the dependencies for this script:

```bash
pip install wheel
pip install -r requirements.txt
```

Now you are ready to run the script.

IMPORTANT: When you are done using the script, make sure to deactivate the `virtualenv` by running the `deactivate` command.

```bash
# Deactivates virtualenv and stops isolating dependencies.
deactivate
```

Otherwise your other python scripts may not work.

## Usage

Once you have activated the `virtualenv`, use the script as follows:

```bash
python3 tcga_fpkm_dendrogram.py <filename>
```

A folder called `results` will be created which will contain the following output files:
