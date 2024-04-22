import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import { Construct } from 'constructs';
import * as iam from 'aws-cdk-lib/aws-iam'

export class EventBridgeLambdaStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Lambda function
    const myEventBus = new events.EventBus(this, 'MyEventBus');
    const role = new iam.Role(this, 'MyLambdaRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('AdministratorAccess'),

        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole'),
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaVPCAccessExecutionRole'),
        // Add more managed policies as needed
      ],
    });

    const myLambda = new lambda.Function(this, 'MyLambda', {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: 'index.lambda_handler',
      code: lambda.Code.fromAsset('./bin/index.zip'),
      role:role
    });

    // EventBridge rule with custom event pattern
    const myRule = new events.Rule(this, 'MyRule', {
      eventPattern: {
        "detailType": ["AWS Service Event Via CloudTrail"],
        "detail": {
          "eventSource": ["secretsmanager.amazonaws.com"],
          "eventName": ["DeleteSecret"]
   } 
  }});
  myRule.addTarget(new targets.LambdaFunction(myLambda));
  myRule.addTarget(new targets.EventBus(myEventBus));



  const rule2 = new events.Rule(this, 'Rule2', {
    eventPattern: {
      "detailType": ["AWS API Call via CloudTrail"],
      "detail": {
        "eventSource": ["iam.amazonaws.com"],
        "eventName": [
          "DeleteUser",
          "CreateUser",
          "DeleteRole",
          "CreateRole",
          "DeleteRolePolicy",
          "PutRolePolicy",
          "DeletePolicy",
          "CreatePolicy"
        ]
      }
    },
  });
  rule2.addTarget(new targets.LambdaFunction(myLambda));
  // rule2.addTarget(new targets.EventBus(myEventBus))


  const rule3 = new events.Rule(this, 'Rule3', {
    eventPattern: {
      "detailType": ["AWS API Call via CloudTrail"],
      "detail": {
        "eventSource": ["rds.amazonaws.com"],
        "eventName": [
          "StopDBInstance",
      "DeleteDBInstance"
        ]
      }
    },
  });
  rule3.addTarget(new targets.LambdaFunction(myLambda));
  // rule3.addTarget(new targets.EventBus(myEventBus))

  const rule4 = new events.Rule(this, 'Rule4', {
    eventPattern: {
      "detailType": ["AWS API Call via CloudTrail"],
      "detail": {
        "eventSource": ["s3.amazonaws.com"],
        "eventName": ["DeleteBucket"],
        "requestParameters": {
          "bucketName": [{ "prefix": "audit" }]
        }
      }
    },
  });
  rule4.addTarget(new targets.LambdaFunction(myLambda));
  // rule4.addTarget(new targets.EventBus(myEventBus))

  const rule5 = new events.Rule(this, 'Rule5', {
    eventPattern: {
      "detailType": ["AWS Service Event Via CloudTrail"],
      "detail": {
        "eventSource": ["kms.amazonaws.com"],
        "eventName": [
          "DisableKey",
          "EnableKey",
          "UpdateKeyDescription",
          "ScheduleKeyDeletion",
          "DeleteKey"
        ]
      }
    },
  });
  rule5.addTarget(new targets.LambdaFunction(myLambda));
  // rule5.addTarget(new targets.EventBus(myEventBus))

  }

}

const app = new cdk.App();
new EventBridgeLambdaStack(app, 'EventBridgeLambdaStack125');
app.synth();