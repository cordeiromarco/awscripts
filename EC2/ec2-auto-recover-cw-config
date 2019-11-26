#! /bin/bash
REGION='ap-northeast-1'
for INSTANCE_ID in `aws ec2 describe-instances --region $REGION | jq '.Reservations[].Instances[].InstanceId ' | cut -d '"' -f 2`
do
  echo $INSTANCE_ID
  aws cloudwatch put-metric-alarm --alarm-name "recover-instance ".$INSTANCE_ID  --alarm-description "Recover Instance"  --namespace AWS/EC2 --dimensions Name=InstanceId,Value=$INSTANCE_ID --statistic Average  --metric-name StatusCheckFailed_System --comparison-operator GreaterThanThreshold --threshold 0 --period 60 --evaluation-periods 2 --alarm-actions arn:aws:automate:$REGION:ec2:recover --region $REGION

done
