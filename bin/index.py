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

def lambda_handler(event,context):

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

    print(event)

