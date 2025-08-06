library(tidyverse)

# Load your data
df <- read.csv("/Users/dlforrister/Downloads/batch55DIA_iimn_gnps_quant_full.csv")  # Or read.csv() if it's a CSV

# Define ID columns to keep
id_cols <- c("id", "area", "rt", "mz_range:min", "mz_range:max", "rt_range:min",
             "rt_range:max", "mz", "intensity_range:min", "intensity_range:max",
             "height", "charge", "fragment_scans", "alignment_scores:rate",
             "alignment_scores:aligned_features_n", "alignment_scores:align_extra_features",
             "alignment_scores:weighted_distance_score", "alignment_scores:mz_diff_ppm",
             "alignment_scores:mz_diff", "alignment_scores:rt_absolute_error",
             "alignment_scores:ion_mobility_absolute_error", 
             "molecular_networking:net_cluster_id", "molecular_networking:net_community_id",
             "molecular_networking:edges", "molecular_networking:net_cluster_size", 
             "molecular_networking:net_community_size")

# Convert to long format
df_long <- df %>%
  pivot_longer(
    cols = starts_with("datafile."),
    names_to = c("datafile", "variable"),
    names_pattern = "datafile\\.([^\\.]+\\.mzML)\\.(.+)",
    values_to = "value",
    values_transform = as.character  # ensure all values are stored as character to avoid type clash
  )

names(df_long)
# Optional: spread variables into wide per datafile
df_clean <- df_long %>%
  pivot_wider(
    names_from = variable,
    values_from = value,
    names_prefix = "datafile_"
  )

TIC_thresh <- 10000

feature_to_find <- df_clean %>% filter(datafile=="RN18_50_371.mzML",datafile_height > TIC_thresh)  %>% select(id,datafile,datafile_mz_range.min,datafile_mz_range.max,datafile_rt_range.min,datafile_rt_range.max)



library(mzR)
library(dplyr)
library(purrr)

datafile = "Emodin_2.mzXML"
datafile = "C1_5.mzML"
# Set path to your mzML files
mzml_path <- "~/Downloads/"  # update this to your directory
get_mzml_file <- function(datafile) file.path(mzml_path, datafile)


mzmin=271.0 
mzmax=271.2
rtmin=10.5*60
rtmax=10.6*60

# Function to extract TIC and UV-Vis spectrum for one feature
extract_feature_data <- function(datafile, mzmin, mzmax, rtmin, rtmax) {
  filepath <- get_mzml_file(datafile)
  
  ms <- openMSfile(filepath, backend = "pwiz")
  hdr <- header(ms)
  
  # Filter scans in RT window and MS1
  scans_in_rt <- hdr$retentionTime >= rtmin & hdr$retentionTime <= rtmax & hdr$msLevel == 1
  
  scan_indices <- which(scans_in_rt)
  
  if (length(scan_indices) == 0) return(NULL)
  
  # Extract spectra
  spectra <- spectra(ms, scan_indices)
  
  # Calculate TIC abundance in m/z window for each scan
  tic_abundances <- map_dbl(spectra, function(sp) {
    idx <- which(sp[, 1] >= mzmin & sp[, 1] <= mzmax)
    sum(sp[idx, 2])
  })
  
  # UV-Vis spectrum (if present, in MS1, may be encoded in extra fields)
  # mzR cannot extract DAD directly from mzML (no native support)
  # So we fake a "UV spectrum" by returning the summed TIC trace in the mz window across time
  rt_vals <- hdr$retentionTime[scan_indices]
  data.frame(
    datafile = datafile,
    rt = rt_vals,
    TIC_in_mz_window = tic_abundances
  )
}

# Apply function to each row in `feature_to_find`
uvvis_data_list <- pmap_dfr(
  feature_to_find,
  function(id, datafile, datafile_mz_range.min, datafile_mz_range.max,
           datafile_rt_range.min, datafile_rt_range.max) {
    message("Processing ", datafile, " | ID: ", id)
    df <- extract_feature_data(
      datafile,
      as.numeric(datafile_mz_range.min),
      as.numeric(datafile_mz_range.max),
      as.numeric(datafile_rt_range.min),
      as.numeric(datafile_rt_range.max)
    )
    df$feature_id <- id
    df
  }
)




library(rawrr)

# Path to Thermo .raw file
rawfile <- "D:/data/yourfile.raw"

# List available scan metadata (includes PDA if available)
scan_info <- readIndex(rawfile)

# Read PDA scan by number
uv_scan <- readChromatogram(rawfile, type = "uv")  # PDA trace

# Optionally, plot it
plot(uv_scan$time, uv_scan$intensity, type = "l", main = "PDA Chromatogram")



library(arrow)
df_p <- read_parquet("~/Downloads/test_uv_vis_parquet/C1_5.parquet")
names(df_p)

table(df_p$MsOrder)
View(df_p)


###
install.packages("remotes")
remotes::install_github("https://github.com/ethanbass/chromatographR/")

library(chromatographR)

library(chromConverter)

UV_VIS_1 <- chromConverter::read_mzml("~/Downloads/test_uv_vis/C1_5.mzML")
dat <- chromConverter::read_chroms("~/Downloads/test_uv_vis/C1_5.mzML", format_in = "mzml")

dat$C1_5$DAD

data("Sa_warp")
Sa_warp



# Convert to wide format: rt as rows, lambda as columns
uv_matrix <- dcast(uv_dt, rt ~ lambda, value.var = "intensity")


# Optionally convert to a matrix (removing the rt column from data)
uv_mat <- as.matrix(uv_matrix[, -1])
rownames(uv_mat) <- uv_matrix$rt
uv_mat[1:10,1:10]


tpoints <- as.numeric(rownames(uv_mat))
lambda <- '400'
 
matplot(x = tpoints, y = uv_mat[,lambda],type = 'l', ylab = 'Abs (mAU)', xlab = 'Time (min)')
matplot(x = tpoints, y = ptw::baseline.corr(uv_mat[,lambda], p = .001, lambda = 1e5), type = 'l', add = TRUE, col='blue', lty = 3)


# Convert to data.table if not already
uv_dt <- as.data.table(UV_VIS_1$DAD)

# Define target retention time and tolerance
target_rt <- 12.55  # minutes
tolerance <- 0.5  # minutes

# Subset rows around the retention time
spectrum <- uv_dt[rt >= target_rt - tolerance & rt <= target_rt + tolerance, 
                  .(intensity = mean(intensity)), 
                  by = lambda]

# Plot
ggplot(spectrum, aes(x = lambda, y = intensity)) +
  geom_line() +
  labs(title = paste("UV-Vis Spectrum at ~", target_rt, "min"),
       x = "Wavelength (nm)",
       y = "Mean Absorbance") +
  theme_minimal()


chrom_270 <- uv_dt[lambda == 280]

# Plot intensity over retention time
ggplot(chrom_270, aes(x = rt, y = intensity)) +
  geom_line(color = "blue") +
  labs(title = "UV Chromatogram at 270 nm",
       x = "Retention Time (min)",
       y = "Absorbance (AU)") +
  theme_minimal()




library(chemodiv)
chemodiv::compDis
