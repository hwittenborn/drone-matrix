#!/usr/bin/env bash
set -ex

echo "${proget_api_key}" | docker login -u api \
                                        --password-stdin \
                                        "${proget_server}"

docker build --pull \
             --no-cache \
             --tag "${proget_server}/docker/hwittenborn/drone-matrix" \
             ./

docker push "${proget_server}/docker/hwittenborn/drone-matrix"
