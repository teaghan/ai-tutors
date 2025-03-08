import requests
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import utils.access_codes
import utils.calculator
import utils.config
import utils.display_tutors
import utils.https
import utils.knowledge_files
import utils.logger
import utils.memory_manager
import utils.menu
import utils.modify_index
import utils.password
import utils.save_to_html
import utils.session
import utils.styling
import utils.tutor_data
import utils.user_data
import utils.warmup

import llms.chatbot_llm
import llms.models
import llms.moderator_llm
import llms.tutor_llm

def warm_start():
    port = os.environ.get("PORT", "8501")
    url = f"http://localhost:{port}"
    print(f'Trying to warm up {url}')

    try:
        response = requests.get(url)
        print("Warm-up successful:", response.status_code)
    except Exception as e:
        print("Warm-up failed:", e)

if __name__ == "__main__":
    warm_start()