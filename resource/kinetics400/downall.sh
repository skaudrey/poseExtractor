#!/bin/bash

cd ../../input
mkdir kinetics400

# download path files
wget https://s3.amazonaws.com/kinetics/400/train/k400_train_path.txt
wget https://s3.amazonaws.com/kinetics/400/val/k400_val_path.txt
wget https://s3.amazonaws.com/kinetics/400/test/k400_test_path.txt
# download corrupted file
wget https://s3.amazonaws.com/kinetics/400/replacement_for_corrupted_k400.tgz -O 'replacement_for_corrupted_k400.tgz'

# making directory
mkdir train
mkdir test
mkdir val

# download
bash ./download.sh ./k400_train_path.txt ./train
bash ./download.sh ./k400_test_path.txt ./test
bash ./download.sh ./k400_val_path.txt ./val

# extract
cp ./extract.sh ./train
cd train
bash ./extract.sh ../k400_train_path.txt

cd ../
cp ./extract.sh ./test
cd test
bash ./extract.sh ../k400_test_path.txt

cd ../
cp ./extract.sh ./val
cd val
bash ./extract.sh ../k400_val_path.txt

cd ../

# delete txt, tar and extract.sh
find . -name "*.txt" | xargs rm -rf
cd train
find . -name "*.tar.gz" | xargs rm -rf
find . -name "*.sh" | xargs rm -rf
cd ../

cd test
find . -name "*.tar.gz" | xargs rm -rf
find . -name "*.sh" | xargs rm -rf
cd ../

cd val
find . -name "*.tar.gz" | xargs rm -rf
find . -name "*.sh" | xargs rm -rf
cd ../

# unzip corrupted file and maintain the required directory
mkdir replacement
tar -zxvf ./replacement_for_corrupted_k400.tgz

# get resource file for replacement
wget https://s3.amazonaws.com/kinetics/400/annotations/train.csv -O 'train.csv'
wget https://s3.amazonaws.com/kinetics/400/annotations/test.csv -O 'test.csv'
wget https://s3.amazonaws.com/kinetics/400/annotations/val.csv -O 'val.csv'

# replace corrupted files

# source python if needed
#source ~/envs/python/bin/activate
python ./organizeKinetics.py -a ./train.csv -d ./train -c ./replacement_for_corrupted_k400 -cls False
python ./organizeKinetics.py -a ./test.csv -d ./test -c ./replacement_for_corrupted_k400 -cls False
python ./organizeKinetics.py -a ./val.csv -d ./val -c ./replacement_for_corrupted_k400 -cls False

# clean abudant folder
rm -rf ./replacement

# delete abundant data if you want to make it be clean
#find . -name "*.py" | xargs rm -rf
#find . -name "*.sh" | xargs rm -rf


# after that, the data will be organized as
# ----kinetics400
# --------train
# ------------class1
# ----------------file1.mp4
# ----------------file2.mp4
# ------------class2
# ----------------file1.mp4
# ----------------file2.mp4
# --------test
# --------val




