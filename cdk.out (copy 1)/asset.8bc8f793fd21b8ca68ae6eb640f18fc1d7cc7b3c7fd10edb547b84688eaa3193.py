import boto3


def format_event_table(event):
    # Extract required attributes from the event
    principalId = event.get('userIdentity', {}).get('principalId', '')
    arn = event.get('userIdentity', {}).get('arn', '')
    user = event.get('userIdentity', {}).get('type', '')
    accountId = event.get('userIdentity', {}).get('accountId', '')
    eventTime = event.get('eventTime', '')
    eventSource = event.get('eventSource', '')
    eventName = event.get('eventName', '')
    sourceIPAddress = event.get('sourceIPAddress', '')
    table = f"""
    <table border="1" cellspacing="0" cellpadding="5">
        <tr>
            <th>Attribute</th>
            <th>Value</th>
        </tr>
        <tr>
            <td>Event Time</td>
            <td>{eventTime}</td>
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


    return table

# Example usage
event = {
    "eventVersion": "1.09",
    "userIdentity": {
        "type": "Root",
        "principalId": "120833356027",
        "arn": "arn:aws:iam::120833356027:root",
        "accountId": "120833356027",
        "accessKeyId": "ASIARYIR2WD52S67ZYKZ",
        "sessionContext": {
            "attributes": {
                "creationDate": "2024-04-19T04:03:12Z",
                "mfaAuthenticated": "false"
            }
        }
    },
    "eventTime": "2024-04-19T09:06:43Z",
    "eventSource": "ec2.amazonaws.com",
    "eventName": "CreateSecurityGroup",
    "awsRegion": "ap-south-1",
    "sourceIPAddress": "106.222.202.82",
    "userAgent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "requestParameters": {
        "groupName": "dedeed",
        "groupDescription": "wdefe",
        "vpcId": "vpc-0c044c0cdb0dffede"
    },
    "responseElements": {
        "requestId": "a99beb7f-1f0b-47cc-aa0e-3849e1e458d9",
        "_return": true,
        "groupId": "sg-0efcc20525890441d"
    },
    "requestID": "a99beb7f-1f0b-47cc-aa0e-3849e1e458d9",
    "eventID": "0bcc75d2-93a2-4872-98fb-11c364b5cbfb",
    "readOnly": false,
    "eventType": "AwsApiCall",
    "managementEvent": true,
    "recipientAccountId": "120833356027",
    "eventCategory": "Management",
    "tlsDetails": {
        "tlsVersion": "TLSv1.3",
        "cipherSuite": "TLS_AES_128_GCM_SHA256",
        "clientProvidedHostHeader": "ec2.ap-south-1.amazonaws.com"
    },
    "sessionCredentialFromConsole": "true"
}
def lambda_handler():

    # Create an SES client
    ses = boto3.client('ses', region_name='ap-south-1')

    # Email configurations
    sender_email = 'vishalvinayram5432@gmail.com'
    recipient_email = 'vishalvinayram811@gmail.com'
    subject = 'Report'

    # Create email body with HTML content
    html_body = format_event_table(event)

    # Send email with HTML body
    ses.send_email(
        Destination={'ToAddresses': [recipient_email]},
        Message={
            'Body': {
                'Html': {
                    'Charset': 'UTF-8',
                    'Data': html_body
                }
            },
            'Subject': {
                'Charset': 'UTF-8',
                'Data': subject
            }
        },
        Source=sender_email
    )

    print('Email sent successfully!')

lambda_handler()