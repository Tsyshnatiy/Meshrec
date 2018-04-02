#!/bin/bash

model_path=$1
pano_path=$2

declare -i leave_n=500

train_ratio="0.8"
test_ratio="0.1"

echo "Put files under ROOT/test directory!"

echo "Creating panoramas"
echo "From"
echo $model_path
echo "To"
echo $pano_path 
python ./make_cylinder_projections.py $model_path $pano_path

echo "Removing dublicates from"
echo $pano_path
python ./remove_dublicates.py $pano_path

echo "Filtering similar from"
echo $pano_path
echo "Params are:"
echo "Leaving"
echo $leave_n
python ./filter_similar.py $pano_path $leave_n

echo "Splitting by test, validation and train"
echo "Params:"
echo "Train ratio = "
echo $train_ratio
echo "Test ratio = "
echo $test_ratio
python ./split.py $pano_path $train_ratio $test_ratio

echo "Syncing pano and model dirs"
echo "From"
echo $pano_path
echo "to"
echo $model_path
python ./sync_pano_and_off.py $pano_path $model_path

echo "Finished!"

