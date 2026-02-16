provider "google" {
  project = var.project_id
  region  = var.region
}

# Optional: enable APIs (requires permissions)
resource "google_project_service" "apis" {
  for_each = var.enable_apis ? toset([
    "storage.googleapis.com",
    "pubsub.googleapis.com",
    "bigquery.googleapis.com",
  ]) : toset([])

  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

data "google_project" "this" {
  project_id = var.project_id
}

############################
# GCS bucket + "folder"
############################
resource "google_storage_bucket" "bucket" {
  name                        = var.gcs_bucket_name
  location                    = var.gcs_location
  uniform_bucket_level_access = true
  force_destroy               = var.gcs_force_destroy

  depends_on = [google_project_service.apis]
}

# Create a "folder" by creating an object with that prefix
resource "google_storage_bucket_object" "folder_marker" {
  bucket  = google_storage_bucket.bucket.name
  name    = "${trim(var.gcs_folder_prefix, "/")}/.keep"
  content = "keep"

  depends_on = [google_storage_bucket.bucket]
}

############################
# BigQuery dataset + table
############################
resource "google_bigquery_dataset" "dataset" {
  dataset_id = var.bq_dataset_id
  location   = var.bq_location

  depends_on = [google_project_service.apis]
}

resource "google_bigquery_table" "table" {
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id   = var.bq_table_id

  # Provide schema as JSON string
  schema = var.bq_table_schema_json

  depends_on = [google_bigquery_dataset.dataset]
}

#############################################
# IAM for Pub/Sub to write into BigQuery
#############################################
# If you do NOT set bigquery_config.service_account_email, Pub/Sub uses its service agent:
# service-{project_number}@gcp-sa-pubsub.iam.gserviceaccount.com :contentReference[oaicite:5]{index=5}
locals {
  pubsub_service_agent = "serviceAccount:service-${data.google_project.this.number}@gcp-sa-pubsub.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "pubsub_bq_metadata_viewer" {
  project = var.project_id
  role    = "roles/bigquery.metadataViewer"
  member  = local.pubsub_service_agent

  depends_on = [google_project_service.apis]
}

resource "google_project_iam_member" "pubsub_bq_data_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = local.pubsub_service_agent

  depends_on = [google_project_service.apis]
}

############################
# Pub/Sub topic + subscription
############################
resource "google_pubsub_topic" "topic" {
  name = var.pubsub_topic_name

  depends_on = [google_project_service.apis]
}

resource "google_pubsub_subscription" "bq_subscription" {
  name  = var.pubsub_subscription_name
  topic = google_pubsub_topic.topic.name

  bigquery_config {
    # Provider expects: {projectId}.{datasetId}.{tableId} :contentReference[oaicite:6]{index=6}
    table = "${var.project_id}.${google_bigquery_dataset.dataset.dataset_id}.${google_bigquery_table.table.table_id}"

    # Choose ONE:
    # - use_table_schema: Pub/Sub uses BigQuery table schema; messages must be JSON :contentReference[oaicite:7]{index=7}
    # - use_topic_schema: Pub/Sub uses the topic schema (not created in this example) :contentReference[oaicite:8]{index=8}
    use_table_schema = var.pubsub_use_table_schema
    use_topic_schema = var.pubsub_use_topic_schema

    # Optional behavior (relevant when using topic/table schema) :contentReference[oaicite:9]{index=9}
    write_metadata     = var.pubsub_write_metadata
    drop_unknown_fields = var.pubsub_drop_unknown_fields

    # Optional: specify a custom SA to write to BigQuery; otherwise Pub/Sub service agent is used :contentReference[oaicite:10]{index=10}
    service_account_email = var.pubsub_bigquery_service_account_email != "" ? var.pubsub_bigquery_service_account_email : null
  }

  depends_on = [
    google_bigquery_table.table,
    google_project_iam_member.pubsub_bq_metadata_viewer,
    google_project_iam_member.pubsub_bq_data_editor,
  ]
}