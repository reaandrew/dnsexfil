terraform {
  backend "s3" {
    bucket         = "dnsexfil-demo-terraform-state"
    key            = "state/terraform.tfstate"
    region         = "eu-west-2"
    encrypt        = true
  }
}
