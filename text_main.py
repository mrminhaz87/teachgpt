from claude_api_CS import Client
from manim_exec import *
import os

from dotenv import load_dotenv
load_dotenv()

cookie = os.environ.get('cookie')
claude_api = Client(cookie)
MAX_ITERATION = 5
DEBUG  = True

query = "Integrate xsinx / (1+cos^2x) in range 0 to pi "
theme = "Dark"
accent_color = "Blue"
resolution= "(1920x1080)"
special_instructions = ""

MANIM_PROMPT = f'''#Persona: You are a Manim python code generator. Generate python code only, no other text.

Generate manim visualization for: {query}

# Requirements:
- *Valid manim python code only*
- Scene/class name must be "Scene" 
- Provide solution if topic is a question
- Create logical solution for math/STEM questions
- Provide step by step solution for Math / Physics question
- Make sure to draw within the canvas of resolution {resolution}
- Don't overlapp or cramp up things. Plese clear canvas and then continue if necessary. 
- Use {theme} theme and {accent_color} accent color
- HD video. resolution: {resolution}
- Clean, uncramped visualization
- Use arrows/graphs as needed


# Output Format:
```python {resolution}
{{PYTHON_CODE}}
```

'''


if special_instructions != "" : MANIM_PROMPT += "# Suggestions for the visualization: {special_instructions}"

conversation_id = claude_api.create_new_chat()['uuid']
response = claude_api.send_message(MANIM_PROMPT, conversation_id)

if DEBUG: print(response)
success, message = run_manim_code(response, query)

if DEBUG: print(f'{success =} \n {message =} ')

for i in range(1,MAX_ITERATION):
    if not success:
        response = claude_api.send_message(f'The code has the following error when running, please fix:{message}', conversation_id)
        
        if DEBUG: print(response, query)
            
        if DEBUG: print(f'{success =} \n {message =}')
            
        success, message = run_manim_code(response)

