# Deployment Guide

## AWS Deployment

### Prerequisites
- AWS Account with appropriate permissions
- AWS CLI configured locally
- Docker installed
- Terraform installed (optional but recommended)

### Manual Deployment Steps

#### 1. Create ECR Repository
```bash
aws ecr create-repository --repository-name genai-rag-agent --region us-east-1
```

#### 2. Build and Push Docker Image
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -t genai-rag-agent:latest .

# Tag image
docker tag genai-rag-agent:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/genai-rag-agent:latest

# Push to ECR
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/genai-rag-agent:latest
```

#### 3. Create ECS Cluster
```bash
aws ecs create-cluster --cluster-name genai-cluster --region us-east-1
```

#### 4. Create CloudWatch Log Group
```bash
aws logs create-log-group --log-group-name /ecs/genai-rag-agent --region us-east-1
```

#### 5. Store Secrets
```bash
aws secretsmanager create-secret \
  --name openai-api-key \
  --secret-string '{"api_key":"your_key_here"}' \
  --region us-east-1
```

#### 6. Create Task Definition (JSON)
```json
{
  "family": "genai-rag-agent",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "genai-app",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/genai-rag-agent:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "API_PORT",
          "value": "8000"
        }
      ],
      "secrets": [
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:<account-id>:secret:openai-api-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/genai-rag-agent",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ],
  "executionRoleArn": "arn:aws:iam::<account-id>:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::<account-id>:role/ecsTaskRole"
}
```

Register the task definition:
```bash
aws ecs register-task-definition --cli-input-json file://task-definition.json --region us-east-1
```

#### 7. Create Security Group
```bash
aws ec2 create-security-group \
  --group-name genai-ecs-sg \
  --description "Security group for GenAI ECS tasks" \
  --vpc-id <vpc-id>

# Add ingress rule
aws ec2 authorize-security-group-ingress \
  --group-id <sg-id> \
  --protocol tcp \
  --port 8000 \
  --cidr 0.0.0.0/0
```

#### 8. Create ECS Service
```bash
aws ecs create-service \
  --cluster genai-cluster \
  --service-name genai-service \
  --task-definition genai-rag-agent \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[<subnet-id>],securityGroups=[<sg-id>],assignPublicIp=ENABLED}" \
  --region us-east-1
```

#### 9. Set Up Auto Scaling
```bash
# Register scalable target
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/genai-cluster/genai-service \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 2 \
  --max-capacity 4 \
  --region us-east-1

# Create scaling policy
aws application-autoscaling put-scaling-policy \
  --policy-name genai-scaling-policy \
  --service-namespace ecs \
  --resource-id service/genai-cluster/genai-service \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration file://scaling-policy.json \
  --region us-east-1
```

### Terraform Deployment

Use the provided `deployment/aws_infrastructure.tf`:

```bash
cd deployment

# Initialize Terraform
terraform init

# Plan deployment
terraform plan -var="aws_region=us-east-1" -out=tfplan

# Apply deployment
terraform apply tfplan

# Get outputs
terraform output
```

### Verify Deployment

```bash
# Check service status
aws ecs describe-services \
  --cluster genai-cluster \
  --services genai-service \
  --region us-east-1

# Check running tasks
aws ecs list-tasks \
  --cluster genai-cluster \
  --region us-east-1

# Get task details
aws ecs describe-tasks \
  --cluster genai-cluster \
  --tasks <task-arn> \
  --region us-east-1

# View logs
aws logs tail /ecs/genai-rag-agent --follow
```

## GCP Deployment (Cloud Run)

### Prerequisites
- GCP Project
- gcloud CLI configured
- Cloud Build enabled

### Steps

```bash
# Set project
gcloud config set project <project-id>

# Build and push to GCR
gcloud builds submit --tag gcr.io/<project-id>/genai-rag-agent

# Deploy to Cloud Run
gcloud run deploy genai-rag-agent \
  --image gcr.io/<project-id>/genai-rag-agent \
  --platform managed \
  --region us-central1 \
  --memory 512Mi \
  --cpu 1 \
  --set-env-vars OPENAI_API_KEY=<your-key> \
  --allow-unauthenticated
```

## Azure Deployment (Container Instances)

```bash
# Set resource group
az group create --name genai-rg --location eastus

# Deploy container
az container create \
  --resource-group genai-rg \
  --name genai-api \
  --image mcr.microsoft.com/azuredocs/aci-helloworld \
  --cpu 1 --memory 1 \
  --ports 8000 \
  --environment-variables OPENAI_API_KEY=<your-key>
```

## Monitoring & Maintenance

### CloudWatch Dashboards
```bash
# Create dashboard for metrics
aws cloudwatch put-dashboard \
  --dashboard-name genai-dashboard \
  --dashboard-body file://dashboard.json
```

### Update Application
```bash
# Push new image
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/genai-rag-agent:v2

# Update service
aws ecs update-service \
  --cluster genai-cluster \
  --service genai-service \
  --force-new-deployment
```

### Scale Service
```bash
# Update desired count
aws ecs update-service \
  --cluster genai-cluster \
  --service genai-service \
  --desired-count 4
```

## Troubleshooting

### Task Not Starting
```bash
# Check logs
aws logs get-log-events \
  --log-group-name /ecs/genai-rag-agent \
  --log-stream-name <stream-name>

# Describe task
aws ecs describe-tasks --cluster genai-cluster --tasks <task-arn>
```

### High Latency
- Increase task memory/CPU
- Add more tasks with auto-scaling
- Enable caching for vector DB queries
- Optimize embedding model size

### High Costs
- Reduce desired count
- Use spot instances
- Implement request throttling
- Cache frequently accessed data
