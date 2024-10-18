#!/bin/bash

# Ensure the .streamlit directory exists
mkdir -p ~/.streamlit/

# Update the [server] section in config.toml
if grep -q "\[server\]" ~/.streamlit/config.toml; then
    # Update the existing server settings
    sed -i'' 's/^headless *= *.*/headless = true/' ~/.streamlit/config.toml
    sed -i'' 's/^enableCORS *= *.*/enableCORS = false/' ~/.streamlit/config.toml

    # If the port line doesn't exist, add it
    if ! grep -q "^port" ~/.streamlit/config.toml; then
        echo "port = \$PORT" >> ~/.streamlit/config.toml
    fi
else
    # Append the [server] section if it doesn't exist
    cat <<EOL >> ~/.streamlit/config.toml

[server]
headless = true
enableCORS = false
port = \$PORT
EOL
fi
