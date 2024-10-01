#!/bin/bash

WEBHOOK_URL=$1
BUILD_ID=$2

# Create the JSON payload
payload=$(cat <<EOF
{
  "content": "\`$BUILD_ID\` was successful!"
}
EOF
)

# Send the notification
curl -H "Content-Type: application/json" -d "$payload" "$WEBHOOK_URL"