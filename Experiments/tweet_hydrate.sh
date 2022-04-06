#!/bin/bash
for file in $(ls "EngTweetIds");
do
    if [ -f "HydratedTweets/${file}_hydrated_tweets" ];
    then
        echo "Skipping ${file}"
    else
        echo "Processing file: $file"
        /home/ubuntu/argminer_env/bin/python /home/ubuntu/argminer/Experiments/SMMT/data_acquisition/get_metadata.py -i ~/argminer/Experiments/EngTweetIds/${file} -o ~/argminer/Experiments/HydratedTweets/${file}_hydrated_tweets -k  /home/ubuntu/argminer/Experiments/SMMT/data_acquisition/api_keys.json -m e
        echo "Completed Processing file $file"
    fi
done