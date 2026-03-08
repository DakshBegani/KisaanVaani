import time
import uuid

import boto3
from boto3.dynamodb.conditions import Key
from mypy_boto3_dynamodb import DynamoDBServiceResource


dynamodb: DynamoDBServiceResource = boto3.resource("dynamodb", region_name="ap-south-1")

users_tbl = dynamodb.Table("Users")
msg_tbl = dynamodb.Table("Messages")


def get_or_create_conversation(user_id):
    response = users_tbl.get_item(Key={"user_id": user_id}, ConsistentRead=True)
    user = response.get("Item")

    if not user:
        conv_id = str(uuid.uuid4())

        user = {
            "user_id": user_id,
            "active_conversation_id": conv_id,
            "voice_reply": True,
            "created_at": int(time.time()),
        }

        users_tbl.put_item(Item=user)
        return conv_id, user

    conv_id = user.get("active_conversation_id")

    if not conv_id:
        conv_id = str(uuid.uuid4())
        users_tbl.update_item(
            Key={"user_id": user_id},
            UpdateExpression="SET active_conversation_id = :c",
            ExpressionAttributeValues={":c": conv_id},
        )
        user["active_conversation_id"] = conv_id

    return conv_id, user


def fetch_recent_messages(conversation_id, limit=20):
    response = msg_tbl.query(
        KeyConditionExpression=Key("conversation_id").eq(conversation_id),
        Limit=limit,
        ScanIndexForward=False,
        ConsistentRead=True,
    )

    items = response.get("Items", [])
    items = list(reversed(items))

    return [{"role": item.get("role"), "text": item.get("text")} for item in items]


def put_message(conversation_id, user_id, role, text, media_type=None, media_uri=None, extra=None):
    extra = extra or {}
    ts = int(time.time() * 1000)

    item = {
        "conversation_id": conversation_id,
        "timestamp": f"ts#{ts}#{uuid.uuid4()}",
        "user_id": user_id,
        "role": role,
        "text": text,
        "created_at": ts,
        "media_type": media_type,
        "media_uri": media_uri,
        **extra,
    }

    msg_tbl.put_item(Item=item)
