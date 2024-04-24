import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import { Construct } from 'constructs';
import * as iam from 'aws-cdk-lib/aws-iam'
import * as ses from 'aws-cdk-lib/aws-ses';


export class SecreatBridgeLambdaStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
      super(scope, id, props);
      const myEventBus = new events.EventBus(this, 'MyEventBus');
      const role = new iam.Role(this, 'MyLambdaRole', {
        assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
        managedPolicies: [
          iam.ManagedPolicy.fromAwsManagedPolicyName('AdministratorAccess'),
  
          iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole'),
          iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaVPCAccessExecutionRole'),
        ],
      });
     
      const myLambda = new lambda.Function(this, 'MyLambdaSecreat', {
        runtime: lambda.Runtime.PYTHON_3_11,
        handler: 'index.lambda_handler',
        code: lambda.Code.fromAsset('./bin/index.zip'),
        role:role
      });
    
      const myRule = new events.Rule(this, 'SecretManagerDeleteRule', {
        eventPattern: {
          "source": ["aws.secretsmanager"],
          "detailType": ["AWS Service Event Via CloudTrail"],
          "detail": {
            "eventSource": ["secretsmanager.amazonaws.com"],
            "eventName": ["DeleteSecret"]
     } 
    }});
    myRule.addTarget(new targets.LambdaFunction(myLambda));
    myRule.addTarget(new targets.EventBus(myEventBus));
  
  
  
    
  
    }
  
  }