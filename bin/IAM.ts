import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import { Construct } from 'constructs';
import * as iam from 'aws-cdk-lib/aws-iam'
import * as ses from 'aws-cdk-lib/aws-ses';



export class IAMBridgeLambdaStack extends cdk.Stack {
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
      const emailToBeVerified = cdk.Fn.sub("brocoder21@gmail.com")  
      // Create SES identity
      const emailIdentity = new ses.EmailIdentity(this, 'EmailIdentity', {
        identity: ses.Identity.email(emailToBeVerified)
      });
  
      const myLambda = new lambda.Function(this, 'MyIAMLambad', {
        runtime: lambda.Runtime.PYTHON_3_11,
        handler: 'index.lambda_handler',
        code: lambda.Code.fromAsset('./bin/index.zip'),
        role:role
      });
    
      
  
  
  
    const rule2 = new events.Rule(this, 'IAMActionsRule', {
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
    rule2.addTarget(new targets.EventBus(myEventBus))
  
    }
  
  }