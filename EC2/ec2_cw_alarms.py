#!/usr/local/bin/python3
import boto3
#import json
import logging
import os
import sys
logger = logging.getLogger()
logger.setLevel(logging.INFO)
region = "us-west-2"
sns_topic_name = ""
# region = os.environ["AWS_REGION"]
# sns_topic_name = os.environ["SNS_TOPIC_NAME"]

session = boto3.session.Session(profile_name="saml")
ec2 = session.resource("ec2", region_name=region)
cw = session.client("cloudwatch", region_name=region)


def get_detail_type(event):
    try:
        return event["detail-type"]
    except (KeyError, Exception) as e:
        logger.exception(e)
        sys.exit(1)


def get_instance_id(event):
    try:
        return event["detail"]["EC2InstanceId"]
    except (KeyError, Exception) as e:
        logger.exception(e)
        sys.exit(1)


def get_instance_name(instance_id):
    instance = ec2.Instance(instance_id)
    for tag in instance.tags:
        if tag["Key"] == "Name":
            name = tag["Value"]
    if name:
        return f"{name}-{instance_id}"
    else:
        return f"{instance_id}"


def create_cw_cpu_alarm(instance_id, instance_name):
    cw.put_metric_alarm(
        AlarmName=f"{instance_name}_CPU_Utilization_(Lambda)",
        AlarmDescription="CPU Utilization",
        ActionsEnabled=True,
        AlarmActions=[sns_topic_name],
        OKActions=[sns_topic_name],
        MetricName="CPUUtilization",
        Namespace="AWS/EC2",
        Statistic="Average",
        Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
        Period=60,
        EvaluationPeriods=15,
        DatapointsToAlarm=10,
        Threshold=95.0,
        ComparisonOperator="GreaterThanOrEqualToThreshold",
    )


def create_cw_memory_alarm(instance_id, instance_name):
    cw.put_metric_alarm(
        AlarmName=f"{instance_name}_Memory_Utilization_(Lambda)",
        AlarmDescription="MemoryUtilization ",
        ActionsEnabled=True,
        AlarmActions=[sns_topic_name],
        OKActions=[sns_topic_name],
        MetricName="mem_used_percent",
        Namespace="CWAgent",
        Statistic="Average",
        Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
        Period=60,
        EvaluationPeriods=10,
        DatapointsToAlarm=7,
        Threshold=95,
        ComparisonOperator="GreaterThanOrEqualToThreshold",
    )


def create_cw_disk_alarm(instance_id, instance_name):
    cw.put_metric_alarm(
        AlarmName=f"{instance_name}_DiskSpace_Utilization_(Lambda)",
        AlarmDescription="DiskSpaceUtilization ",
        ActionsEnabled=True,
        AlarmActions=[sns_topic_name],
        OKActions=[sns_topic_name],
        MetricName="disk_used_percent",
        Namespace="CWAgent",
        Statistic="Average",
        Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
        Period=60,
        EvaluationPeriods=5,
        DatapointsToAlarm=3,
        Threshold=95,
        ComparisonOperator="GreaterThanOrEqualToThreshold",
    )


def bootstrap_cw_alarms():
    instances = ec2.instances.filter(
        Filters=[{"Name": "tag:Environment", "Values": ["dev"]}]
    )
    for instance in instances:
        for tag in instance.tags:
            if tag["Key"] == "Name":
                name = tag["Value"]
                instance_name = f"{name}-{instance.id}"
                create_cw_cpu_alarm(instance.id, instance_name)
                create_cw_memory_alarm(instance.id, instance_name)
                create_cw_disk_alarm(instance.id, instance_name)


def delete_cw_alarms(alarms):
    try:
        cw.delete_alarms(AlarmNames=alarms)
    except Exception as e:
        logger.exception(f"Failed to delete CloudWatch alarms: {e}")
        sys.exit(1)


def lambda_handler(event, context):
    logger.info(f"Event: {str(event)}")
    detail_type = get_detail_type(event)
    instance_id = get_instance_id(event)
    instance_name = get_instance_name(instance_id)
    if detail_type == "EC2 Instance Launch Successful":
        logger.info(
            "EC2 Instance Launch Successful.  Creating CloudWatch alarms.")
        create_cw_cpu_alarm(instance_id, instance_name)
        create_cw_memory_alarm(instance_id, instance_name)
        create_cw_disk_alarm(instance_id, instance_name)
    elif detail_type == "EC2 Instance Terminate Successful":
        logger.info(
            "EC2 Instance Terminate Successful.  Deleting CloudWatch alarms.")
        alarms = [
            f"{instance_name}_CPU_Utilization_(Lambda)",
            f"{instance_name}_Memory_Utilization_(Lambda)",
            f"{instance_name}_DiskSpace_Utilization_(Lambda)",
        ]
        delete_cw_alarms(alarms)
    else:
        logger.info("Bootstrapping CloudWatch alarms for existing instances.")
        bootstrap_cw_alarms()
