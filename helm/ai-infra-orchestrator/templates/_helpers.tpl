{{- define "ai-infra-orchestrator.name" -}}
ai-infra-orchestrator
{{- end -}}

{{- define "ai-infra-orchestrator.fullname" -}}
{{ include "ai-infra-orchestrator.name" . }}
{{- end -}}
