from sklearn.cluster import AgglomerativeClustering
from sklearn.decomposition import PCA
import scipy.cluster.hierarchy as shc
import plotly.figure_factory as ff
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import shutil
import sys
import os

# Create and save TCGA-FPKM static dendrogram & patient assigned cluster colors
def plot_dendro_static(data, labels):
    plt.figure(figsize=(10, 7))
    plt.title("TCGA-FPKM: Dendrogram")
    result = shc.dendrogram(shc.linkage(data, method='ward'))
    plt.savefig('./results/TCGA-FPKM_dendrogram-stat.png')
    plt.show()
    
    leaf_colors = {}
    color_tcga = {}
    missed_tcga = patient_labels[845]

    for i in range(len(result['color_list'])):
        leaf_colors[result['leaves'][i]] = result['color_list'][i]

    for j in range(len(patient_labels)):
        if j != 845:
            color_tcga[patient_labels[j]] = leaf_colors[j]

    df = pd.DataFrame({'Patient': list(color_tcga.keys()), 
                        'Cluster_color': list(color_tcga.values())})
    df.to_csv('./results/TCGA-FPKM_cluster-colors.csv', index=False)
    
# Create and save TCGA-FPKM interactive dendrogram
def plot_dendro_interactive(data, labels):
    data_array = tcga_data.to_numpy()
    fig = ff.create_dendrogram(data_array, orientation='left', labels=labels)
    fig.update_layout(width=1600, height=800)
    fig.write_image('./results/TCGA-FPKM_dendrogram-intr.png')
    fig.show()

# Create and save TCGA-FPKM patient instances clustered into n clusters
def gen_clusters(n, data, labels):
    cluster = AgglomerativeClustering(n_clusters=n, affinity='euclidean', 
                                        linkage='ward')
    cluster.fit_predict(data)
    clusters = cluster.labels_.tolist()

    df = pd.DataFrame(list(zip(labels, clusters)), 
                        columns =['Patient', 'Cluster'])
    df.to_csv('./results/TCGA-FPKM_Cluster.csv', index=False)

# Create and save 2-component PCA analysis scatter plot of TCGA-FPKM data
def gen_scatter(data):
        features = list(tcga_data.columns)
        x = tcga_data.loc[:, features].values

        pca = PCA(n_components=2)
        principalComponents = pca.fit_transform(x)
        principalDf = pd.DataFrame(data = principalComponents
                , columns = ['principal component 1', 'principal component 2'])

        principalDf.plot.scatter(x='principal component 1', 
                                    y='principal component 2', 
                                    title= "TCGA-FPKM: 2 Component PCA")
        plt.savefig('./results/TCGA-FPKM_pca_scatter.png')
        plt.show(block=True)

#################################### MAIN #####################################
if __name__ == "__main__":
    # Check command-line argument
    if (len(sys.argv) < 2):
        print('missing input file name argument')
        sys.exit()

    # Check file validity
    filename = str(sys.argv[1])
    if (filename.split('.')[-1] != 'csv'):
        print('input file is invalid type (not .csv)')
        sys.exit()
    
    # Create directory for results
    path = './results'
    if (os.path.isdir(path)):
        shutil.rmtree(path)
    os.mkdir(path)

    # Reading in TCGA data
    tcga_df = pd.read_csv(filename)
    patient_labels = tcga_df.columns[1:]
    tcga_data = tcga_df.drop(columns=['sample']).transpose()

    # Plotting static dendrogram
    plot_dendro_static(tcga_data, patient_labels)
    
