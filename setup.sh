#!/bin/bash

# Ensure the .streamlit directory exists
mkdir -p ~/.streamlit/

# Use sed to update or add the necessary server configurations for Heroku
if grep -q "\[server\]" ~/.streamlit/config.toml; then
    # Modify the existing [server] section
    sed -i '' 's/^port.*/port = $PORT/' ~/.streamlit/config.toml
    sed -i '' 's/^headless.*/headless = true/' ~/.streamlit/config.toml
    sed -i '' 's/^enableCORS.*/enableCORS = false/' ~/.streamlit/config.toml
else
    # Append the [server] section if it doesn't exist (just in case)
    cat <<EOL >> ~/.streamlit/config.toml

[server]
headless = true
enableCORS = false
port = \$PORT
EOL
fi
