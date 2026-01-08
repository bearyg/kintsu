#!/bin/bash
echo "Creating Eventarc trigger for Takeout Uploads..."

gcloud eventarc triggers create trigger-mbox-upload-dev \
  --location=us-central1 \
  --destination-run-service=kintsu-worker-mbox-dev \
  --destination-run-region=us-central1 \
  --event-filters="type=google.cloud.storage.object.v1.finalized" \
  --event-filters="bucket=kintsu-hopper-kintsu-gcp" \
  --service-account=351476623210-compute@developer.gserviceaccount.com

echo "Trigger creation command sent."
