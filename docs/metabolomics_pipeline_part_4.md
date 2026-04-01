# <div align="center"> Part 4: Post Processing W/ Sirius and dreaMS </div>

[← Back to Main README](../README.md)


## Table of Contents
  - [Overview of POD Diskspace and Storage](#overview-of-pod-diskspace-and-storage)
  - [Notes on Important Group Folders](notes-on-important-group-folders)


## Processing MGF files in dreams

### 1. Activating the dreams evironment calculting the embeddings from an MGF

Step 1: Activate dreams

```bash
conda activate /stor/work/Sedio/dreams

```

To Run Dreams you have to use python. Once conda dreams is activated you can just type python and your bash terminal will open python

```bash
python
```

```python
#Calculate dreams embeddings from Panama MGF file. Note this is the GNPS MGF so spectra have been clustered to have one spectra per feature
from dreams.api import dreams_embeddings
import numpy as np
from dreams.utils.data import MSData
import h5py

```
## Note we should use the gnps version of the mgf because this already includes concensus spectra (one per featureID)

hdf5 file will be auto generated when you load MS file with DreaMS.
```python
h5_path = "/stor/work/Sedio/UPLCMS_Data/POD_Pipeline_Demo_Data/demo_carya_10k_20220822_gnps.hdf5"
mgf_path = "/stor/work/Sedio/UPLCMS_Data/POD_Pipeline_Demo_Data/demo_carya_10k_20220822_gnps.mgf"

embs = dreams_embeddings(mgf_path)

def add_column_to_hdf5(h5_path, column_data, column_name):
    """
    Adds or overwrites a column in the top-level of a DreaMS-compatible HDF5 file.

    Parameters:
        h5_path (str or Path): Path to the HDF5 file.
        column_data (array-like): The data to store (e.g. 1D or 2D NumPy array).
        column_name (str): The name of the column/dataset.
    """
    with h5py.File(h5_path, "a") as f:
        if column_name in f:
            del f[column_name]
        f.create_dataset(column_name, data=column_data)

add_column_to_hdf5(h5_path, embs, "DreaMS_embedding")
```

```python
#Step 3: #now embeddings can be reloaded from the HDF5 file using the MSData class  
# Load your existing MSData file (with spectra)

#Example of how to work with the MSData object
msdata = MSData.load(h5_path)

#This tells you what columns are available in the MSData object.
msdata.columns() 

#get values from a specfic column, e.g., 'FEATURE_ID' or 'FORMULA'
msdata.get_values('MSLEVEL')[1:10]

#get emeddings from a specfic column, e.g., 'FEATURE_ID' or 'FORMULA'
msdata.get_values('DreaMS_embedding')  # Or msdata['FORMULA']

#msdata is now an object in memory. To close...
del msdata
```

### 2. Annotate MS with library matching

In this step, we'll use the DreaMS embeddings for library matching to annotate the query spectra.

```python
import pandas as pd
import numpy as np
from pathlib import Path
from tqdm import tqdm
from sklearn.metrics.pairwise import cosine_similarity
from dreams.utils.data import MSData
from dreams.api import dreams_embeddings
from dreams.definitions import *
```

Load your query dataset and the library with pre-computed DreaMS embeddings.

You can download the library file [here (MassSpecGym_DreaMS.hdf5)](https://huggingface.co/datasets/roman-bushuiev/GeMS/blob/main/data/auxiliary/MassSpecGym_DreaMS.hdf5) (We have already downloaded see below).

```python
# Load your query data (the HDF5 file processed in the previous step)
# NOTE: The .mgf file is converted to .hdf5 after computing embeddings
in_pth = Path("/stor/work/Sedio/UPLCMS_Data/POD_Pipeline_Demo_Data/demo_carya_10k_20220822_gnps.hdf5")
# Load the library data
lib_pth = Path('/stor/work/Sedio/UPLCMS_Data/POD_Pipeline_Demo_Data/MassSpecGym_DreaMS.hdf5')

msdata_query = MSData.load(in_pth)
embs_query = msdata_query[DREAMS_EMBEDDING]

msdata_lib = MSData.load(lib_pth)
embs_lib = msdata_lib[DREAMS_EMBEDDING]

print('Shape of the query embeddings:', embs_query.shape)
print('Shape of the library embeddings:', embs_lib.shape)
```

Compute the cosine similarity between the query and library embeddings.

```python
sims = cosine_similarity(embs_query, embs_lib)
```

Choose the top-k candidates with the highest similarity for each query spectrum.

```python
k = 5
topk_cands = np.argsort(sims, axis=1)[:, -k:][:, ::-1]
```

Organize the results into a `DataFrame` and save to a CSV file.

```python
df = []
for i, topk in enumerate(tqdm(topk_cands)):
    for n, j in enumerate(topk):
        df.append({
            'query_feature_id': i + 1,
            'query_precursor_mz': msdata_query.get_values(PRECURSOR_MZ, i),
            'topk_hit': n + 1,
            'library_SMILES': msdata_lib.get_smiles(j),
            'library_ID': msdata_lib.get_values('IDENTIFIER', j),
            'DreaMS_similarity': sims[i, j],
        })

df = pd.DataFrame(df)
df.to_csv('/stor/work/Sedio/UPLCMS_Data/POD_Pipeline_Demo_Data/library_matching_results.csv', index=False)
print(df.head)
```

-----

### 3. Molecular networking

Use the DreaMS embeddings to construct a molecular network.

```python
import networkx as nx
from sklearn.neighbors import kneighbors_graph
```

Build a k-nearest neighbor (k-NN) graph using `kneighbors_graph`.

```python
k = 3  # Number of nearest neighbors
thld = 0.7  # DreaMS similarity threshold

# Build k-NN graph from DreaMS embeddings
A = kneighbors_graph(embs_query, k, mode='distance', metric='cosine', include_self=False)
A = A.toarray()

# Threshold the graph and invert cosine distances to similarities
for i in range(A.shape[0]):
    for j in range(A.shape[1]):
        if A[i, j] != 0:
            A[i, j] = 1 - A[i, j]
        if A[i, j] < thld:
            A[i, j] = 0

# Initialize a networkx graph from the adjacency matrix
G = nx.from_numpy_array(A)
```

Populate the network with node and edge metadata.

```python
# Add node attributes
for i in tqdm(G.nodes(), desc='Adding node attributes'):
    G.nodes[i]['precursor_mz'] = msdata_query.get_values(PRECURSOR_MZ, i)
    G.nodes[i]['scan_number'] = i + 1 # Assuming scan number corresponds to index

# Add edge attributes
for u, v in tqdm(G.edges(), desc='Adding edge attributes'):
    G[u][v]['DreaMS_similarity'] = G[u][v]['weight']
    del G[u][v]['weight']
```

Export the resulting network to `Cytoscape` for visualization.

```python
nx.write_graphml(G, '/stor/work/Sedio/UPLCMS_Data/POD_Pipeline_Demo_Data/molecular_network.graphml')
```
It's sad that we should download [Cytoscape](https://cytoscape.org/) to visulize this graph.

Open Cytoscape --> click File --> Import --> Network from File --> find this file
<img width="2396" height="1580" alt="image" src="https://github.com/user-attachments/assets/84fcc898-e9a5-4392-848d-b7e3a471254b" />

-----

### 4. Clustering MS/MS spectra with LSH (4-5 are optional sections)

Perform fast clustering of MS/MS spectra using Locality-Sensitive Hashing (LSH) to identify highly similar or near-duplicate spectra.

```python
from dreams.algorithms.lsh import BatchedPeakListRandomProjection
```

Initialize the LSH algorithm.

```python
# bin_step defines the width of the m/z binning window.
# n_hyperplanes specifies the number of hyperplanes used to split the space.
lsh_projector = BatchedPeakListRandomProjection(bin_step=0.5, n_hyperplanes=50)
```

Compute the LSH hashes for the spectra.

```python
spectra = msdata_query.get_spectra()
lshs = lsh_projector.compute(spectra)
```

Associate the LSH hashes with your data for further analysis.

```python
# Add the LSH hashes as a new column to the HDF5 file
add_column_to_hdf5(in_pth, lshs, "LSH_HASH")

# You can inspect the number of clusters by counting the unique hashes
unique_lshs = np.unique(lshs)
print(f'Number of spectra: {len(lshs)}')
print(f'Number of LSH clusters: {len(unique_lshs)}')
```

-----

### 5. Assessing spectral quality

Apply MS/MS single-spectrum quality metrics from DreaMS to filter out low-quality spectra.

```python
from dreams.utils.dformats import DataFormatA
from dreams.utils.io import append_to_stem
```

Subject each spectrum to quality control checks.

```python
spectra = msdata_query.get_spectra()
prec_mzs = msdata_query.get_values(PRECURSOR_MZ)

dformat = DataFormatA()
quality_lvls = [dformat.val_spec(s, p, return_problems=True) for s, p in zip(spectra, prec_mzs)]

# Check how many spectra passed all filters
quality_counts = pd.Series(quality_lvls).value_counts()
print(quality_counts)
```

Create a new dataset containing only the high-quality spectra.

```python
# Define path for the output high-quality file
hq_pth = append_to_stem(in_pth, 'high_quality').with_suffix('.hdf5')

# Pick only high-quality spectra and save them to `hq_pth`
msdata_query.form_subset(
    idx=np.where(np.array(quality_lvls) == 'All checks passed')[0],
    out_pth=hq_pth
)

# Try reading the new file to verify
msdata_hq = MSData.load(hq_pth)
print(f"Number of high-quality spectra: {len(msdata_hq)}")
```


## Using screen
Use screen for longer jobs such as sirius runs. This will allow you to disconnect from the server while the job is still running. 


Create a new named screen
```{bash}
screen -S sirius_test_run_screen_03-19-26
```

While commands are running in the screen you can detach from it with "Ctrl + A" and then "D"

Reattach to the named screen with:
```{bash}
screen -r sirius_test_run_screen_03-19-26
```

While in a screen session you can enter "copy mode" with "Ctrl + A", and then "Esc". This willn allow you to scroll up if needed

If reconnecting to a screen session is not working try: 
```{bash}
screen -xr 
```
To terminate a screen session when you are finished use "exit" while attached to the screen
```{bash}
exiit
```

## Run SIRIUS

Activate the SIRIUS conda environment 

```{bash}
conda activate /stor/work/Sedio/conda_envs/sirius622
```
```{bash}
sirius -h 
```
Login to SIRIUS 

```{bash}
sirius login -u example@gmail.com -p
```

SIRIUS login status/account can be checked with:

```{bash}
sirius login --show 
```



Run SIRIUS. These are the parameters that the Invasive Species Lab used, but we are still refining out parameters 
Required inputs:

--input: path to the .mgf file you will be using

--project: path to the .sirius project file. This file will be created if it does not exist already

--output: path to where you would like output files to be written

formulas: # need to expand this section. In the meantime run
```{bash}
sirius formulas --help
```

Start SIRIUS run

```{bash}
sirius \
    --input ~/working/G067/output/g067_dr_sirius.mgf \
    --project ~/working/G067/output/sirius_output/g067_dr_project.sirius \
    --cores 24 \ 
    spectra-search \
    formulas -p orbitrap -I [M+H]+ -i [M+Na]+,[M+K]+ --ppm-max 5 --ppm-max-ms2 10 \ 
    zodiac \
    fingerprint \
    canopus \
    structures --db pubchem,metacyc,bio,chebi,gnps,hmdb,hsdb,kegg,knapsack,lotus,lipidmaps,maconda,mesh,mimedb,norman,plantcyc,pubchemannotationbio,        pubchemannotationdrug,pubchemannotationfood,pubchemannotationsafetyandtoxic,pubmed,supernatural,teromol,ymdb \ 
    denovo-structures \
    write-summaries --top-k-summary 10 --output ~/working/G067/output/sirius_output/
```




