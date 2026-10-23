# 1. RDS Security Group
resource "aws_security_group" "rds_sg" {
  name        = "rds-security-group"
  description = "Allow inbound traffic from ECS tasks only"
  vpc_id      = var.vpc_id
  
  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [var.ecs_sg_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "rds-sg"
  }
}

# 2. Establish RDS MySQL Database Instance
resource "aws_db_instance" "my_db" {
  identifier             = "my-inventory-db"
  allocated_storage      = 20
  max_allocated_storage  = 100
  engine                 = "mysql"
  engine_version         = "8.0"
  instance_class         = "db.t4g.micro"

  # Following settings (three lines) are for test/practice environment only.
  backup_retention_period = 0  # Disable automatic backups for the test environment to avoid unnecessary storage costs.
  skip_final_snapshot = true   # Skip the final snapshot to facilitate easier cleanup in the test environment.      
  deletion_protection = false  # Disable deletion protection to allow for easier resource cleanup in the test environment.
  

  db_name                = "inventory_db"
  username               = "admin"
  password               = var.db_password
  publicly_accessible    = true
    
  vpc_security_group_ids = [aws_security_group.rds_sg.id]  
  db_subnet_group_name = "main-rds-subnet-group-k8s"
  
  tags = {
    Name = "my-production-db"
  }
}

