import rpy2.robjects as ro

print(ro.r('R.home()'))
print(ro.r('R.version.string'))

print(ro.r('.libPaths()'))
print(ro.r('renv::status()'))

ro.r.source("alt_setup.R")
