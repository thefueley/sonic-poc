#!/bin/sh

WEBHOOK_URL=$1
MESSAGE=$2

# Create the JSON payload
payload=$(cat <<EOF
{
  "content": "$MESSAGE"
}
EOF
)

# Send the notification
curl -H "Content-Type: application/json" -d "$payload" "$WEBHOOK_URL"