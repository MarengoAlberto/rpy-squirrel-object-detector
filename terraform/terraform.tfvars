project_id = "my-gcp-project"
region     = "us-central1"

gcs_bucket_name    = "my-unique-bucket-name-12345"
gcs_location       = "US"
gcs_folder_prefix  = "data/incoming"
gcs_force_destroy  = false

bq_dataset_id = "events_ds"
bq_table_id   = "events"

pubsub_topic_name        = "events-topic"
pubsub_subscription_name = "events-to-bq"

pubsub_use_table_schema  = true
pubsub_use_topic_schema  = false
pubsub_write_metadata    = true
pubsub_drop_unknown_fields = true

# pubsub_bigquery_service_account_email = "optional-custom-writer@my-gcp-project.iam.gserviceaccount.com"