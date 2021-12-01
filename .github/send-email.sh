#!/bin/bash

echo test > thing.txt
echo '{"thing":5}' | jq '.thing'


# run: aws s3 cp thing.txt s3://"$S3_BUCKET_NAME"/thing/txt