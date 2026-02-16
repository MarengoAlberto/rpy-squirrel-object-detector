variable "project_id" { type = string }
variable "region"     { type = string }

variable "enable_apis" {
  type        = bool
  description = "Enable required APIs (storage/pubsub/bigquery)."
  default     = true
}

# GCS
variable "gcs_bucket_name" { type = string }
variable "gcs_location" {
  type    = string
  default = "US"
}
variable "gcs_folder_prefix" {
  type        = string
  description = "Prefix to represent a folder (e.g., data/incoming)."
  default     = "data/incoming"
}
variable "gcs_force_destroy" {
  type    = bool
  default = false
}

# BigQuery
variable "bq_dataset_id" { type = string }
variable "bq_table_id"   { type = string }
variable "bq_location" {
  type    = string
  default = "US"
}

variable "bq_table_schema_json" {
  type        = string
  description = "BigQuery table schema as a JSON string."
  # Default schema works well with use_table_schema = true and write_metadata = true
  # (metadata fields are optional but must exist if write_metadata=true) :contentReference[oaicite:11]{index=11}
  default = <<SCHEMA
[
  {"name":"subscription_name","type":"STRING","mode":"NULLABLE"},
  {"name":"message_id","type":"STRING","mode":"NULLABLE"},
  {"name":"publish_time","type":"TIMESTAMP","mode":"NULLABLE"},
  {"name":"data","type":"JSON","mode":"NULLABLE"},
  {"name":"attributes","type":"JSON","mode":"NULLABLE"}
]
SCHEMA
}

# Pub/Sub
variable "pubsub_topic_name"        { type = string }
variable "pubsub_subscription_name" { type = string }

variable "pubsub_use_table_schema" {
  type        = bool
  description = "Use BigQuery table schema (messages must be JSON)."
  default     = true
}
variable "pubsub_use_topic_schema" {
  type        = bool
  description = "Use Pub/Sub topic schema (not configured in this example). Must not be true at same time as use_table_schema."
  default     = false
}
variable "pubsub_write_metadata" {
  type    = bool
  default = true
}
variable "pubsub_drop_unknown_fields" {
  type    = bool
  default = true
}

variable "pubsub_bigquery_service_account_email" {
  type        = string
  description = "Optional custom service account email for Pub/Sub to write to BigQuery. Leave empty to use Pub/Sub service agent."
  default     = ""
}