import boto3
import json
from datetime import datetime


def lambda_handler(events,context):
    event = events['detail']
    ses = boto3.client('ses', region_name='ap-south-1')

    # Email configurations
    sender_email = 'vishalvinayram5432@gmail.com'
    recipient_email = 'vishalvinayram811@gmail.com'
    user = event.get('userIdentity', {}).get('type', '')

    # Create email body with HTML content
        # Extract required attributes from the event
    userIdentity = event['userIdentity']
    user = userIdentity['type']
    accountId = userIdentity['accountId']
    eventTime = event.get('eventTime')
    eventSource = event['eventSource']
    eventName = event['eventName']
    sourceIPAddress = event['sourceIPAddress']
    datetime_obj = datetime.strptime(eventTime, '%Y-%m-%dT%H:%M:%SZ')

# Convert datetime object to the desired format 'dd-mm-yyyy hh:mm:ss'
    formatted_timestamp = datetime_obj.strftime('%d-%m-%Y %H:%M:%S')

    subject = f'Latest event from  {accountId}'
    table = f"""
    <table border="1" cellspacing="0" cellpadding="5">
        <tr>
            <th>Attribute</th>
            <th>Value</th>
        </tr>
        <tr>
            <td>Event Time</td>
            <td>{formatted_timestamp}</td>
        </tr>
        <tr>
            <td>User</td>
            <td>{user}</td>
        </tr>
        <tr>
            <td>Account ID</td>
            <td>{accountId}</td>
        </tr>
        <tr>
            <td>Resource</td>
            <td>{eventSource}</td>
        </tr>
        <tr>
            <td>Change</td>
            <td>{eventName}</td>
        </tr>
    </table>
    """
    ses.send_email(
        Destination={'ToAddresses': [recipient_email]},
        Message={
            'Body': {
                'Html': {
                    'Charset': 'UTF-8',
                    'Data': table
                }
            },
            'Subject': {
                'Charset': 'UTF-8',
                'Data': subject
            }
        },
        Source=sender_email
    )

