###############################################################################
# main.tf  –  VPC + EC2 + Route 53 DNS Firewall + CloudWatch + default tags
###############################################################################
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.35.0"
    }
  }
}

provider "aws" {
  region = "eu-west-2"

  # Default tags applied to every AWS resource
  default_tags {
    tags = {
      Project     = "dns-exfil-demo"
      Environment = "demo"
      Owner       = "andrew.rea"
      ManagedBy   = "terraform"
    }
  }
}

######################
# VPC & Networking
######################

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags                 = { Name = "dns-firewall-demo-vpc" }
}

resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "dns-firewall-demo-gw" }
}

resource "aws_subnet" "public_a" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "eu-west-2a"
  map_public_ip_on_launch = true
  tags                    = { Name = "public-subnet-a" }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }
  tags = { Name = "dns-firewall-public-rt" }
}

resource "aws_route_table_association" "a" {
  subnet_id      = aws_subnet.public_a.id
  route_table_id = aws_route_table.public.id
}

######################
# Security Group
######################

resource "aws_security_group" "ec2_sg" {
  name        = "dns-ec2-sg"
  description = "Allow SSH and all outbound"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

######################
# Key Pair (key material)
######################

resource "aws_key_pair" "default" {
  key_name   = "dns-firewall-key"
  public_key = file(var.public_key_path)
}

######################
# EC2 AMI lookup
######################
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "architecture"
    values = ["x86_64"]
  }

  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

######################
# EC2 Instance
######################

resource "aws_instance" "dns_demo" {
  ami                         = data.aws_ami.amazon_linux.id
  instance_type               = "m5.large"
  subnet_id                   = aws_subnet.public_a.id
  associate_public_ip_address = true
  key_name                    = aws_key_pair.default.key_name
  vpc_security_group_ids      = [aws_security_group.ec2_sg.id]

  tags = { Name = "dns-firewall-test-instance" }
}

######################
# CloudWatch log group
######################

resource "aws_cloudwatch_log_group" "dns_query_logs" {
  name              = "/aws/route53resolver/dns-queries"
  retention_in_days = 30
}

#############################
# Route 53 Resolver query log
#############################

resource "aws_route53_resolver_query_log_config" "dns_logging" {
  name            = "vpc-dns-logs"
  destination_arn = aws_s3_bucket.dns_log_bucket.arn
}

resource "aws_route53_resolver_query_log_config_association" "assoc" {
  resolver_query_log_config_id = aws_route53_resolver_query_log_config.dns_logging.id
  resource_id                  = aws_vpc.main.id
}

######################
# DNS Firewall
######################

resource "aws_route53_resolver_firewall_rule_group" "default" {
  name = "vpc-dns-firewall"
}

resource "aws_route53_resolver_firewall_domain_list" "blocked_domains" {
  name    = "blocked-domains"
  domains = ["example-malware.com", "bad-domain.test"]
}

resource "aws_route53_resolver_firewall_rule" "block" {
  name                    = "block-malicious"
  firewall_rule_group_id  = aws_route53_resolver_firewall_rule_group.default.id
  firewall_domain_list_id = aws_route53_resolver_firewall_domain_list.blocked_domains.id
  priority                = 1
  action                  = "BLOCK"
  block_response          = "NODATA"
}

resource "aws_route53_resolver_firewall_rule_group_association" "assoc" {
  name                   = "firewall-assoc"
  firewall_rule_group_id = aws_route53_resolver_firewall_rule_group.default.id
  vpc_id                 = aws_vpc.main.id
  priority               = 200   # 101-9900; 100 is reserved
  mutation_protection    = "DISABLED"
}
