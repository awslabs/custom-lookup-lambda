#!/usr/bin/env bash
echo -n "Enter the S3 Bucket to hold lambda package > "
read S3Bucket
FILE="$(uuidgen)"
pip install -r requirements.txt -t "$PWD"
aws cloudformation package --template-file lambda-cloudformation.yaml --s3-bucket $S3Bucket --s3-prefix custom-lookup/codebuild --output-template-file $FILE
aws cloudformation deploy --template-file $FILE --stack-name custom-lookup-lambda --capabilities CAPABILITY_NAMED_IAM
rm $FILE