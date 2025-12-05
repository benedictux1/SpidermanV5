#!/bin/bash
# This script will help identify what's missing
echo "Checking for essential files..."
files=(
  "app/utils/database.py"
  "app/models/user.py"
  "app/models/contact.py"
  "app/models/note.py"
  "app/utils/chromadb_client.py"
  "app/services/ai_service.py"
  "app/services/contact_service.py"
  "app/services/note_service.py"
  "app/api/auth.py"
  "app/api/contacts.py"
  "app/api/notes.py"
)

for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    echo "✅ $file"
  else
    echo "❌ $file MISSING"
  fi
done
