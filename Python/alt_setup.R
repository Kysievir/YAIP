print(.libPaths())
# The following cannot overwrite existing ricu for some reason.
# devtools::install_local("/home/boat/R_projects/ricu/", force = TRUE)

# Probably this will be chosen again in importr("ricu")
devtools::load_all("/home/boat/R_projects/ricu/")

Sys.setenv(RICU_DATA_PATH = "/home/boat/R_projects/importing_mimic_with_ricu/data/")
Sys.setenv(RICU_CONFIG_PATH = "/home/boat/R_projects/importing_mimic_with_ricu/custom_config/")

source("../ricu-extensions/callbacks/callback-icu-mortality.R")
source("../ricu-extensions/callbacks/callback-kdigo.R")
source("../ricu-extensions/callbacks/callback-sepsis.R")
  
# concept_path <- file.path("..", "ricu-extensions", "configs", c("chemistry", "circulatory", "demographics", "hematology", "medications", "misc", "outcomes", "output", "vitals"))
# dict <- load_dictionary(cfg_dirs = concept_path)

print("setup finished")