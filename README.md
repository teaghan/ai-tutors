# AI Tutors

[Visit AI Tutors](https://www.ai-tutors.ca/)

## About

AI Tutors is an open-source platform that empowers educators to create, customize, and share AI-powered learning tools designed specifically for student use. Built with teacher expertise at its core, our platform leverages Large Language Models (LLMs) to foster critical thinking, creativity, and deeper subject understanding for middle and high school students.

## Key Features

- **Teacher-Created AI Tools**: Easily build and share dependable AI tutoring resources aligned with your teaching philosophy
- **Intelligent Moderation**: Every tutor includes a sophisticated moderator that ensures all responses align with educational guidelines
- **Collaborative Platform**: Build upon the work of other educators and share your own creations
- **Responsible AI Use**: Designed to promote ethical AI application in educational settings


## Python API

First, [build an AI Tutor](https://www.ai-tutors.ca/teacher_start) and **create an access code** for your tutor.

Then install our Python API:

```
pip install ai-tutors
```

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

For detailed usage examples, see our [API usage guide](./examples/api_usage.ipynb).
