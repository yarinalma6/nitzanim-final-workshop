terraform {
  backend "s3" {
    bucket = "nitzanim-tf-state-yarin-noa"
    key    = "terraform.tfstate"
    region = "us-east-1"
  }
}