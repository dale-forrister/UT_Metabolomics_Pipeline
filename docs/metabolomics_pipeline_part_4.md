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

```{pyton}
embs = dreams_embeddings('/stor/work/Sedio/UPLCMS_Data/POD_Pipeline_Demo_Data/demo_carya_10k_20220822_sirius.mgf')

h5_path ="/stor/work/AMDG_SedioLab/UT_dreaMS_NPclassifier/data/npclassifier_mass_spec_gym/Massspec_gym_NPClassifier_All_Smiles_Output.hdf5"

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
