# AI Tutors

A Python client for interacting with AI Tutors through a REST API.

## Installation

```bash
pip install ai_tutors
```

## Usage

### Basic Usage

```python
from ai_tutors import AITutor

# Create a tutor instance with your access code
tutor = AITutor(access_code="your-access-code")

# Display information about your tutor
tutor.display_tutor_info()

# Ask your tutor a question
response = tutor.get_response("What is the Pythagorean theorem?")

# Start a new conversation
tutor.reset_chat()

# Ask another question
response = tutor.get_response("Could you explain neural networks?")
```

### Advanced Usage

```python
# View the full conversation history
message_history = tutor.get_message_history()
for message in message_history:
    print(f"{message['role']}: {message['content']}")

# Customize the API endpoint
custom_tutor = AITutor(
    access_code="your-access-code",
    verbose=False  # Set to False to disable automatic printing of responses
)
```

## API Endpoints

The client communicates with the following API endpoints:

- `GET /`: API information and status
- `GET /tutor_info`: Returns tutor information for a given access code
- `POST /query`: Processes queries to the AI tutor

## Client Methods

- `get_response(prompt, restart_chat=False)`: Get a response from the tutor
- `reset_chat()`: Reset the conversation
- `get_message_history()`: Get the full conversation history
- `display_tutor_info()`: Display information about the tutor
- `load_tutor_info()`: Load or refresh tutor information

## Client Attributes

After initialization, the AITutor client contains the following attributes with information about the tutor:

- `instructions`: Instructions that guide the tutor's behavior
- `guidelines`: Guidelines for the tutor to follow
- `introduction`: The tutor's introduction message
- `knowledge`: The knowledge base of the tutor
- `description`: Description of the tutor
- `availability`: Information about the tutor's availability
- `tool_name`: Name of the tutor
- `teacher_email`: Email of the teacher who created the tutor

## Requirements

- Python 3.8+
- requests
- pandas
- IPython (for Jupyter notebook support)

## Jupyter Notebook Support

The client provides enhanced formatting when used in Jupyter notebooks, automatically displaying responses in Markdown format. 