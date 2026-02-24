# Terraform modules (skeleton)

These modules are placeholders you can wire to your cloud provider / on-prem environment.

- `modules/network`  : VPC/VNet, subnets, routing, NAT, firewall rules
- `modules/kubernetes`: EKS/GKE/AKS or kubeadm-based bootstrap
- `modules/storage`  : block/object/file primitives + CSI dependencies

In regulated envs, prefer:
- remote state (S3 + DynamoDB or Terraform Cloud)
- policy checks (OPA/Conftest) in CI
- change approvals for prod
