import re
import subprocess
import tempfile
import os

def run_manim_code(text, name):
    # Extract Python code from the text
    match = re.search(r'```python\n(.*?)\n```', text, re.DOTALL)
    if not match:
        return False, "No Python code found"

    code = match.group(1)
    
    # Filter name to ensure it's a valid filename
    name = re.sub(r'\W+', '_', name).strip('_')
    
    with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False) as f:
        f.write(code)
        temp_file = f.name

    try:
        # Ensure output directory exists
        os.makedirs('movie', exist_ok=True)

        # Construct and run the Manim command
        cmd = (
            f'/home/cipher/anaconda3/envs/manim/bin/python -m manim render {temp_file} Scene '
            f'-o "{name[:20]}" --media_dir ./my-video-generator/public/movie --disable_caching --flush_cache '
            f'-v ERROR --progress_bar none'
        )
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        return True, result.stdout + result.stderr
    except subprocess.CalledProcessError as e:
        return False, f"Error: {e.stdout}\n{e.stderr}"
    finally:
        # Cleanup temporary file
        if os.path.exists(temp_file):
            os.unlink(temp_file)
