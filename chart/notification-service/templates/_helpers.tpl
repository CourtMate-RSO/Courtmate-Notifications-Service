{{/* Helm template helpers for notification-service */}}
{{- define "notification-service.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- define "notification-service.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name (include "notification-service.name" .) | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end -}}