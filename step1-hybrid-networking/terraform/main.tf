terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "ap-northeast-2"
}

# 1. VPC 생성
resource "aws_vpc" "hybrid_vpc" {
  cidr_block           = "10.100.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "enterprise-hybrid-vpc"
    Environment = "production"
  }
}

# 2. Private Subnet (워크로드용)
resource "aws_subnet" "private_workload" {
  vpc_id            = aws_vpc.hybrid_vpc.id
  cidr_block        = "10.100.1.0/24"
  availability_zone = "ap-northeast-2a"

  tags = {
    Name = "subnet-private-workload-a"
  }
}

# 3. Transit Gateway 연동용 서브넷 (/28)
resource "aws_subnet" "tgw_attachment_subnet" {
  vpc_id            = aws_vpc.hybrid_vpc.id
  cidr_block        = "10.100.254.0/28"
  availability_zone = "ap-northeast-2a"

  tags = {
    Name = "subnet-tgw-attach-a"
  }
}

# 4. Transit Gateway 리소스
resource "aws_ec2_transit_gateway" "main_tgw" {
  description                     = "Enterprise Central Transit Gateway"
  amazon_side_asn                 = 64512
  auto_accept_shared_attachments = "enable"

  tags = {
    Name = "central-tgw"
  }
}

# 5. VPC to TGW Attachment 연결
resource "aws_ec2_transit_gateway_vpc_attachment" "vpc_tgw_attach" {
  transit_gateway_id = aws_ec2_transit_gateway.main_tgw.id
  vpc_id             = aws_vpc.hybrid_vpc.id
  subnet_ids         = [aws_subnet.tgw_attachment_subnet.id]

  tags = {
    Name = "tgw-attachment-hybrid-vpc"
  }
}