# ==========================================
# 1. ECS Task Role (for FastApi/boto3)
# ==========================================
resource "aws_iam_role" "ecs_task_role" {
  name = "my-ecs-task-role-k8s"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

# ==========================================
# 2. ECS Task Execution IAM Role (for AWS ECS Agent)
# ==========================================
resource "aws_iam_role" "ecs_execution_role" {
  name = "ecs-execution-role-k8s"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

# 2a. Load AWS official ECS Task Execution policy)
resource "aws_iam_role_policy_attachment" "ecs_execution_role_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# 2b. Least privilege policy: Only allow ECS Execution Role to read the "exclusive" DB secret ARN to inject into environment variables
resource "aws_iam_policy" "ecs_execution_secrets_policy" {
  name        = "ecs-execution-secrets-db-only-k8s"
  description = "Allow ECS Execution Role to pull specific DB secret from Secrets Manager"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["secretsmanager:GetSecretValue"]
        Resource = "*"
      }
    ]
  })
}

# 2c.Mounted to the Execution Role (for ECS Agent upgrades/environmental changes)
resource "aws_iam_role_policy_attachment" "attach_secrets_to_execution" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = aws_iam_policy.ecs_execution_secrets_policy.arn
}

# 2d. Mounted to a Task Role (used by Python boto3 code)
resource "aws_iam_role_policy_attachment" "attach_secrets_to_task_role" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = aws_iam_policy.ecs_execution_secrets_policy.arn
}
# ==========================================
# 3. ECS Cluster
# ==========================================
resource "aws_ecs_cluster" "main_cluster" {
  name = "my-app-cluster"
}

# ==========================================
# 4. ECS Task Definition
# ==========================================
resource "aws_ecs_task_definition" "app_task" {
  family                   = "my-app-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "my-app-container"
      image     = "${aws_ecr_repository.app_repo.repository_url}:latest"
      essential = true

      portMappings = [
        {
          containerPort = 80
          hostPort      = 80
          protocol      = "tcp"
        }]     
          
      # Insensitive control items are retained in the environment section.
      environment = [
        { name = "DB_HOST", value = aws_db_instance.my_db.address },
        { name = "DB_NAME", value = "inventory_db" },
        { name = "DB_USER", value = "admin" }
      ]
      # Security Best Practices: Sensitive passwords should not be written in plaintext; 
      # they should be dynamically injected via Secrets Manager through secrets.      
      secrets = [
        {
          name      = "DB_PASSWORD"
          valueFrom = "${aws_secretsmanager_secret.db_secret.arn}:DB_PASSWORD::"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/my-app"
          "awslogs-region"        = "ap-northeast-1"
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}

# ==========================================
# 5. CloudWatch Log Group
# ==========================================
resource "aws_cloudwatch_log_group" "ecs_log_group" {
  name              = "/ecs/my-app-k8s"
  retention_in_days = 7
}

# ==========================================
# 6. ECS Service
# ==========================================
resource "aws_ecs_service" "main" {
  name            = "my-ecs-service"
  cluster         = aws_ecs_cluster.main_cluster.id
  task_definition = aws_ecs_task_definition.app_task.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = module.vpc.public_subnet_ids
    security_groups  = [module.alb.ecs_sg_id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = module.alb.target_group_arn
    container_name   = "my-app-container"
    container_port   = 80
  }

  depends_on = [module.alb.alb_listener_http]
}

# ==========================================
# 7. Secrets Manager Secret Container
# ==========================================
resource "aws_secretsmanager_secret" "db_secret" {
  name                    = "prod/inventory/db-credentials-k8s"  
  recovery_window_in_days = 0 # The test environment is set to 0 to facilitate immediate deletion.
}

# =====================================================================
# 8. Secret Version (Write database password and connection information)
# ======================================================================
resource "aws_secretsmanager_secret_version" "db_secret_val" {
  secret_id     = aws_secretsmanager_secret.db_secret.id
  secret_string = jsonencode({
    DB_USER     = "admin"                      
    DB_PASSWORD = var.db_password               
    DB_HOST     = aws_db_instance.my_db.address 
    DB_NAME     = "inventory_db"
    DB_PORT     = 3306
  })
}