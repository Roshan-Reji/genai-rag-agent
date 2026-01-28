"""
AWS deployment configuration using boto3
"""
import boto3
import json
from typing import Dict, Optional


class AWSDeploymentManager:
    """Manage AWS deployment for GenAI RAG Agent"""
    
    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self.ecr_client = boto3.client('ecr', region_name=region)
        self.ecs_client = boto3.client('ecs', region_name=region)
        self.cloudwatch = boto3.client('cloudwatch', region_name=region)
    
    def create_ecr_repository(self, repo_name: str = "genai-rag-agent") -> Dict:
        """Create ECR repository"""
        try:
            response = self.ecr_client.create_repository(repositoryName=repo_name)
            return response
        except self.ecr_client.exceptions.RepositoryAlreadyExistsException:
            print(f"Repository {repo_name} already exists")
            return None
    
    def get_ecr_login_token(self) -> Dict:
        """Get ECR login token"""
        response = self.ecr_client.get_authorization_token()
        return response['authorizationData'][0]
    
    def create_ecs_cluster(self, cluster_name: str = "genai-cluster") -> Dict:
        """Create ECS cluster"""
        response = self.ecs_client.create_cluster(
            clusterName=cluster_name,
            clusterSettings=[
                {
                    'name': 'containerInsights',
                    'value': 'enabled'
                }
            ]
        )
        return response
    
    def register_task_definition(
        self,
        task_family: str = "genai-rag-agent",
        container_image: str = None,
        cpu: str = "256",
        memory: str = "512"
    ) -> Dict:
        """Register ECS task definition"""
        if not container_image:
            raise ValueError("container_image is required")
        
        response = self.ecs_client.register_task_definition(
            family=task_family,
            networkMode='awsvpc',
            requiresCompatibilities=['FARGATE'],
            cpu=cpu,
            memory=memory,
            containerDefinitions=[
                {
                    'name': 'genai-app',
                    'image': container_image,
                    'portMappings': [
                        {
                            'containerPort': 8000,
                            'hostPort': 8000,
                            'protocol': 'tcp'
                        }
                    ],
                    'environment': [
                        {'name': 'API_PORT', 'value': '8000'},
                        {'name': 'DEBUG', 'value': 'false'}
                    ],
                    'secrets': [
                        {
                            'name': 'OPENAI_API_KEY',
                            'valueFrom': 'arn:aws:secretsmanager:us-east-1:ACCOUNT:secret:openai-key'
                        }
                    ],
                    'logConfiguration': {
                        'logDriver': 'awslogs',
                        'options': {
                            'awslogs-group': '/ecs/genai-rag-agent',
                            'awslogs-region': self.region,
                            'awslogs-stream-prefix': 'ecs'
                        }
                    },
                    'healthCheck': {
                        'command': ['CMD-SHELL', 'curl -f http://localhost:8000/health || exit 1'],
                        'interval': 30,
                        'timeout': 5,
                        'retries': 3,
                        'startPeriod': 60
                    }
                }
            ]
        )
        return response
    
    def create_ecs_service(
        self,
        cluster_name: str,
        service_name: str = "genai-service",
        task_definition: str = "genai-rag-agent",
        desired_count: int = 2,
        subnets: list = None,
        security_groups: list = None
    ) -> Dict:
        """Create ECS service"""
        if not subnets or not security_groups:
            raise ValueError("subnets and security_groups are required")
        
        response = self.ecs_client.create_service(
            cluster=cluster_name,
            serviceName=service_name,
            taskDefinition=task_definition,
            desiredCount=desired_count,
            launchType='FARGATE',
            networkConfiguration={
                'awsvpcConfiguration': {
                    'subnets': subnets,
                    'securityGroups': security_groups,
                    'assignPublicIp': 'ENABLED'
                }
            },
            deploymentConfiguration={
                'maximumPercent': 200,
                'minimumHealthyPercent': 100,
                'deploymentCircuitBreaker': {
                    'enable': True,
                    'rollback': True
                }
            },
            tags=[
                {'key': 'Application', 'value': 'GenAI-RAG-Agent'},
                {'key': 'Environment', 'value': 'Production'}
            ]
        )
        return response
    
    def setup_cloudwatch_alarms(self, service_name: str) -> None:
        """Setup CloudWatch alarms"""
        self.cloudwatch.put_metric_alarm(
            AlarmName=f'{service_name}-cpu-high',
            ComparisonOperator='GreaterThanThreshold',
            EvaluationPeriods=2,
            MetricName='CPUUtilization',
            Namespace='AWS/ECS',
            Period=300,
            Statistic='Average',
            Threshold=80.0,
            ActionsEnabled=True,
            Dimensions=[
                {'Name': 'ServiceName', 'Value': service_name},
                {'Name': 'ClusterName', 'Value': 'genai-cluster'}
            ]
        )
        
        self.cloudwatch.put_metric_alarm(
            AlarmName=f'{service_name}-memory-high',
            ComparisonOperator='GreaterThanThreshold',
            EvaluationPeriods=2,
            MetricName='MemoryUtilization',
            Namespace='AWS/ECS',
            Period=300,
            Statistic='Average',
            Threshold=80.0,
            ActionsEnabled=True
        )


def create_terraform_config() -> str:
    """Generate Terraform configuration for AWS deployment"""
    terraform_config = """
# AWS Provider
provider "aws" {
  region = var.aws_region
}

# VPC
resource "aws_vpc" "genai" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "genai-vpc"
  }
}

# Subnets
resource "aws_subnet" "genai_public_1" {
  vpc_id                  = aws_vpc.genai.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = {
    Name = "genai-public-subnet-1"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "genai" {
  vpc_id = aws_vpc.genai.id

  tags = {
    Name = "genai-igw"
  }
}

# Security Group
resource "aws_security_group" "genai_ecs" {
  name        = "genai-ecs-sg"
  description = "Security group for GenAI ECS tasks"
  vpc_id      = aws_vpc.genai.id

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "genai-ecs-sg"
  }
}

# ECR Repository
resource "aws_ecr_repository" "genai" {
  name                 = "genai-rag-agent"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "genai-repo"
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "genai_ecs" {
  name              = "/ecs/genai-rag-agent"
  retention_in_days = 30

  tags = {
    Name = "genai-logs"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "genai" {
  name = "genai-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name = "genai-cluster"
  }
}

# ECS Task Definition
resource "aws_ecs_task_definition" "genai" {
  family                   = "genai-rag-agent"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"

  container_definitions = jsonencode([
    {
      name      = "genai-app"
      image     = "${aws_ecr_repository.genai.repository_url}:latest"
      essential = true

      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "API_PORT"
          value = "8000"
        },
        {
          name  = "DEBUG"
          value = "false"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.genai_ecs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])

  tags = {
    Name = "genai-task-def"
  }
}

# ECS Service
resource "aws_ecs_service" "genai" {
  name            = "genai-service"
  cluster         = aws_ecs_cluster.genai.id
  task_definition = aws_ecs_task_definition.genai.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [aws_subnet.genai_public_1.id]
    security_groups  = [aws_security_group.genai_ecs.id]
    assign_public_ip = true
  }

  deployment_configuration {
    maximum_percent         = 200
    minimum_healthy_percent = 100
    deployment_circuit_breaker {
      enable   = true
      rollback = true
    }
  }

  tags = {
    Name = "genai-service"
  }
}

# Auto Scaling Target
resource "aws_appautoscaling_target" "genai_target" {
  max_capacity       = 4
  min_capacity       = 2
  resource_id        = "service/${aws_ecs_cluster.genai.name}/${aws_ecs_service.genai.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

# Auto Scaling Policy
resource "aws_appautoscaling_policy" "genai_policy" {
  policy_type            = "TargetTrackingScaling"
  resource_id            = aws_appautoscaling_target.genai_target.resource_id
  scalable_dimension     = aws_appautoscaling_target.genai_target.scalable_dimension
  service_namespace      = aws_appautoscaling_target.genai_target.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value = 70.0

    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }

    scale_down_cooldown = 300
    scale_up_cooldown   = 60
  }
}

# Outputs
output "ecr_repository_url" {
  value = aws_ecr_repository.genai.repository_url
}

output "ecs_service_name" {
  value = aws_ecs_service.genai.name
}

output "cloudwatch_log_group" {
  value = aws_cloudwatch_log_group.genai_ecs.name
}
"""
    return terraform_config


if __name__ == "__main__":
    # Example usage
    manager = AWSDeploymentManager(region="us-east-1")
    
    # Create resources
    print("Creating ECR repository...")
    manager.create_ecr_repository()
    
    print("Creating ECS cluster...")
    manager.create_ecs_cluster()
    
    print("\nTerraform configuration generated")
    tf_config = create_terraform_config()
    with open("deployment/aws_infrastructure.tf", "w") as f:
        f.write(tf_config)
