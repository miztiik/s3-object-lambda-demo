
#!/bin/bash
set -ex

AWS_PROFILE="elf"
AWS_REGION="us-east-2"
LAYER_NAME1="awsXrayLayer5F64DDB8"
LAYER_NAME2="requestsLayerBF8AC11D"
LAYER_VERSION=4



# for i in {1..4}
# do
#     echo "Deleting Layer: LAYER_NAME1 Version: $i"
#     aws lambda delete-layer-version --profile $AWS_PROFILE --region $AWS_REGION --layer-name LAYER_NAME1 --version-number $i
#     aws lambda delete-layer-version --profile $AWS_PROFILE --region $AWS_REGION --layer-name LAYER_NAME2 --version-number $i
# done

function delete_layers(){
    # for i in {1..4}
    for i in $(seq $2 -1 1)
        do
            echo "Deleting Layer: $1 Version: $i"
            aws lambda delete-layer-version --profile $AWS_PROFILE --region $AWS_REGION --layer-name $1 --version-number $i
        done
}

delete_layers $LAYER_NAME2 $LAYER_VERSION