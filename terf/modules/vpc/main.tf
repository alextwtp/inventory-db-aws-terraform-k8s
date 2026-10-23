# 1.Establish a VPC
resource "aws_vpc" "my_vpc" {
  cidr_block           = "10.0.0.0/16" 
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "main-vpc"
  }
}

# 2. Establish Public Subnet (for ALB / ECS deployment)
resource "aws_subnet" "public_subnet" {
  vpc_id                  = aws_vpc.my_vpc.id
  cidr_block              = "10.0.0.0/24" 
  map_public_ip_on_launch = true
  availability_zone       = "${var.aws_region}a"

  tags = {
    Name = "public-subnet"
  }
}

# 3. Establish Internet Gateway
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.my_vpc.id

  tags = {
    Name = "main-igw"
  }
}

# 4. Establish Route Table and Associate with IGW
resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.my_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "public-route-table"
  }
}

# 5. Associate Route Table with Public Subnet
resource "aws_route_table_association" "public_assoc" {
  subnet_id      = aws_subnet.public_subnet.id
  route_table_id = aws_route_table.public_rt.id
}

# 6. Establish Second Subnet (located in a different AZ, e.g., ap-northeast-2c)
resource "aws_subnet" "public_subnet_2" {
  vpc_id                  = aws_vpc.my_vpc.id
  cidr_block              = "10.0.2.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "${var.aws_region}c" # Note that this is zone c

  tags = {
    Name = "public-subnet-2"
  }
}

# 7. Associate Second Subnet with Route Table
resource "aws_route_table_association" "public_assoc_2" {
  subnet_id      = aws_subnet.public_subnet_2.id
  route_table_id = aws_route_table.public_rt.id
}

# 8. Establish RDS Dedicated DB Subnet Group
resource "aws_db_subnet_group" "rds_subnet_group" {  
  name = "main-rds-subnet-group-k8s"
  subnet_ids = [aws_subnet.public_subnet.id, aws_subnet.public_subnet_2.id]

  tags = {
    Name = "main-rds-subnet-group-k8s"
  }
}
