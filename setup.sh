#!/bin/bash

# Ensure the .streamlit directory exists
mkdir -p ~/.streamlit/

# Append the necessary server settings for Heroku to the existing config.toml
cat <<EOL >> ~/.streamlit/config.toml

# Heroku-specific server settings
[server]
headless = true
enableCORS = false
port = \$PORT
EOL
