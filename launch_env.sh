#!/usr/bin/bash

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1

if [ -z "$REQUIRED_NEOS_VERSION" ]; then
  export REQUIRED_NEOS_VERSION="18"
fi

if [ -z "$AGNOS_VERSION" ]; then
  export AGNOS_VERSION="3"
fi

if [ -z "$PASSIVE" ]; then
  export PASSIVE="1"
fi

export STAGING_ROOT="/data/safe_staging"

if [ -f "/data/params/d/MapboxEnabled" ]; then
    GET_MAPBOX_STAT=$(cat /data/params/d/MapboxEnabled)
    if [ "$GET_MAPBOX_STAT" == "1" ]; then
        export MAPBOX="1"
    else
        touch /data/mapbox_test
    fi
fi