#!/bin/bash

cd ./data/NTU-RGB-D
# download data
wget --no-check-certificate -r 'https://drive.google.com/u/0/uc?id=1CUZnBtYwifVXS21yVg62T-vrPVayso5H&export=download' -O nturgbd_skeletons_s001_to_s017.zip

wget --no-check-certificate -r 'https://drive.google.com/u/0/uc?id=1tEbuaEqMxAV7dNc4fqu1O4M7mC6CJ50w&export=download' -O nturgbd_skeletons_s018_to_s032.zip

wget
# unzip
unzip ./nturgbd_skeletons_s001_to_s017.zip
unzip ./nturgbd_skeletons_s018_to_s032.zip

# delete zip file
rm nturgbd_skeletons_s001_to_s017.zip nturgbd_skeletons_s018_to_s032.zip