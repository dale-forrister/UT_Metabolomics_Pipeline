# <div align="center"> Part 4: Post Processing W/ Sirius and Dreams </div>

[← Back to Main README](../README.md)


## Table of Contents
  - [Overview of POD Diskspace and Storage](#overview-of-pod-diskspace-and-storage)
  - [Notes on Important Group Folders](notes-on-important-group-folders)


## Processing MGF files in dreams

### 1. Activating the dreams evironment calculting the embeddings from an MGF

Step 1: Activate dreams

```{bash}
conda activate /stor/work/Sedio/dreams

```

To Run Dreams you have to use python. Once conda dreams is activated you can just type python and your bash terminal will open python

```{bash}
python
```

```{python}
#Calculate dreams embeddings from Panama MGF file. Note this is the GNPS MGF so spectra have been clustered to have one spectra per feature
from dreams.api import dreams_embeddings
import numpy as np
from dreams.utils.data import MSData
import h5py

```
## Note we should use the gnps version of the mgf because this already includes concensus spectra (one per featureID)

```{pyton}
h5_path ="/stor/work/Sedio/UPLCMS_Data/POD_Pipeline_Demo_Data/demo_carya_10k_20220822_gnps.mgf"

embs = dreams_embeddings(h5_path)

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

add_column_to_hdf5(h5_path, embs, "DREAMS_EMBEDDING")
```
```{python}
#Step 3: #now embeddings can be reloaded from the HDF5 file using the MSData class  
# Load your existing MSData file (with spectra)
h5_path ="/stor/work/AMDG_SedioLab/UT_dreaMS_NPclassifier/data/npclassifier_mass_spec_gym/Massspec_gym_NPClassifier_All_Smiles_Output.hdf5"

#Example of how to work with the MSData object
msdata = MSData.load(h5_path)

#This tells you what columns are available in the MSData object.
msdata.columns() 

#get values from a specfic column, e.g., 'FEATURE_ID' or 'FORMULA'
msdata.get_values('TITLE')[1:10]

#get emeddings from a specfic column, e.g., 'FEATURE_ID' or 'FORMULA'
msdata.get_values('DREAMS_EMBEDDING')  # Or msdata['FORMULA']

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

You can download the library file [here (MassSpecGym_DreaMS.hdf5)](https://huggingface.co/datasets/roman-bushuiev/GeMS/blob/main/data/auxiliary/MassSpecGym_DreaMS.hdf5).

```python
# Load your query data (the HDF5 file processed in the previous step)
# NOTE: The .mgf file is converted to .hdf5 after computing embeddings
in_pth = Path("/stor/work/Sedio/UPLCMS_Data/POD_Pipeline_Demo_Data/demo_carya_10k_20220822_gnps.hdf5")
# Load the library data
lib_pth = Path('/PATH/TO/MassSpecGym_DreaMS.hdf5')

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
df.to_csv('library_matching_results.csv', index=False)
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
nx.write_graphml(G, 'molecular_network.graphml')
```

-----

### 4. Clustering MS/MS spectra with LSH

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

## Run Sirius

Activate the sirius conda environment 

```{bash}
conda activate sirius622
```
```{bash}
sirius -h 
```

#This is a test run that works but we need to do some testing to come up with the full set of parameters to use...
```{bash}
sirius \
  -i /stor/work/Sedio/UPLCMS_Data/POD_Pipeline_Demo_Data/demo_carya_10k_20220822_sirius.mgf \
  --project /stor/work/Sedio/UPLCMS_Data/POD_Pipeline_Demo_Data/sirius_project \
  --cores 12 \ # important or it will gobble up all the cores
  formulas -p orbitrap -I [M+H]+ --ppm-max 5 --ppm-max-ms2 10
```

#write the summaries with the top 10 

```{bash}
sirius -o /stor/work/Sedio/UPLCMS_Data/POD_Pipeline_Demo_Data/sirius_project summaries --top-k-summary 10 --format tsv
```


