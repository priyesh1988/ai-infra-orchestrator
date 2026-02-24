package infra

default allow := false

# Example policy:
# - deny privileged workloads
# - cap replicas in prod unless explicitly approved
# - allow dev broadly

allow {
  input.environment != "prod"
  not input.changes.privileged
}

allow {
  input.environment == "prod"
  input.replicas <= 10
  not input.changes.privileged
}

reason := "Denied by default policy" {
  not allow
}

constraints := {"max_replicas": 10} {
  input.environment == "prod"
}
