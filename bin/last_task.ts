#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { LastTaskStack } from '../lib/last_task-stack';

const app = new cdk.App();
new LastTaskStack(app, 'LastTaskStack');
