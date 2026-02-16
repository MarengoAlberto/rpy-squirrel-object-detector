output "bucket_name" {
  value = google_storage_bucket.bucket.name
}

output "folder_marker_object" {
  value = google_storage_bucket_object.folder_marker.name
}

output "pubsub_topic" {
  value = google_pubsub_topic.topic.name
}

output "pubsub_subscription" {
  value = google_pubsub_subscription.bq_subscription.name
}

output "bigquery_dataset" {
  value = google_bigquery_dataset.dataset.dataset_id
}

output "bigquery_table" {
  value = google_bigquery_table.table.table_id
}