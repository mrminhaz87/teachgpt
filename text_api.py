from fastapi import FastAPI, Query, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, Dict
from claude_api_CS import Client
from manim_exec import *
import os
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import logging
import shutil
import asyncio
from concurrent.futures import ThreadPoolExecutor
import uuid
from datetime import datetime, timedelta

from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize thread pool
THREAD_POOL = ThreadPoolExecutor(max_workers=4)  # Adjust based on your server capacity

# Job tracking
class JobStatus:
    def __init__(self):
        self.status = "pending"
        self.result = None
        self.error = None
        self.created_at = datetime.now()

# Global job storage with cleanup
class JobStore:
    def __init__(self):
        self.jobs: Dict[str, JobStatus] = {}
        self.lock = asyncio.Lock()
        
    async def cleanup_old_jobs(self):
        async with self.lock:
            current_time = datetime.now()
            jobs_to_remove = [
                job_id for job_id, job in self.jobs.items()
                if (current_time - job.created_at) > timedelta(hours=1)
            ]
            for job_id in jobs_to_remove:
                del self.jobs[job_id]

job_store = JobStore()

# Initialize Claude API with connection pool
class ClaudeAPIPool:
    def __init__(self, pool_size=4):
        self.pool_size = pool_size
        self.cookie = os.environ.get('cookie')
        self.clients = [Client(self.cookie) for _ in range(pool_size)]
        self._current = 0
        self.lock = asyncio.Lock()
    
    async def get_client(self):
        async with self.lock:
            client = self.clients[self._current]
            self._current = (self._current + 1) % self.pool_size
            return client

claude_pool = ClaudeAPIPool()

# Input models
class InputParams(BaseModel):
    query: str = Field(..., description="Query for the visualization")
    name: Optional[str] = Field(None, max_length=50, description="Custom name for the visualization")
    theme: str = Field("Dark", description="Theme of the visualization")
    accent_color: str = Field("Blue", description="Accent color")
    resolution: str = Field("(920x1080", description="Resolution of the output")
    special_instructions: Optional[str] = Field("", description="Special instructions for the visualization")

class JobResponse(BaseModel):
    job_id: str
    status: str

# Background task handler
async def process_visualization(job_id: str, params: InputParams):
    try:
        # Get Claude client from pool
        claude_client = await claude_pool.get_client()
        
        # Construct Manim Prompt
        visualization_name = params.name if params.name else params.query[:50]
        manim_prompt = construct_manim_prompt(params, visualization_name)
        
        # Create conversation and get response
        conversation_id = claude_client.create_new_chat()['uuid']
        response = claude_client.send_message(manim_prompt, conversation_id)
        
        # Execute Manim code
        success, message = await asyncio.get_event_loop().run_in_executor(
            THREAD_POOL, 
            run_manim_code,
            response,
            visualization_name
        )
        
        # Update job status
        async with job_store.lock:
            if success:
                job_store.jobs[job_id].status = "completed"
                job_store.jobs[job_id].result = {"success": True, "filename": f"{visualization_name}.mp4"}
            else:
                job_store.jobs[job_id].status = "failed"
                job_store.jobs[job_id].error = message
                
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {str(e)}")
        async with job_store.lock:
            job_store.jobs[job_id].status = "failed"
            job_store.jobs[job_id].error = str(e)

# Endpoints
@app.post("/generate", response_model=JobResponse)
async def generate_visualization(params: InputParams, background_tasks: BackgroundTasks):
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    # Initialize job status
    async with job_store.lock:
        job_store.jobs[job_id] = JobStatus()
    
    # Schedule the background task
    background_tasks.add_task(process_visualization, job_id, params)
    
    return JobResponse(job_id=job_id, status="pending")

@app.get("/job/{job_id}")
async def get_job_status(job_id: str):
    # Clean up old jobs periodically
    await job_store.cleanup_old_jobs()
    
    # Check job status
    async with job_store.lock:
        job = job_store.jobs.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {
            "status": job.status,
            "result": job.result,
            "error": job.error
        }

@app.delete("/video/{filename}")
async def delete_video(filename: str):
    try:
        base_dir = Path("./my-video-generator/public/movie/videos")
        if not base_dir.exists():
            base_dir = Path("public/movie/videos")
        
        if not base_dir.exists():
            raise HTTPException(status_code=500, detail=f"Videos directory not found")

        # Define synchronous search function
        def search_video_sync():
            for video_dir in base_dir.iterdir():
                if not video_dir.is_dir():
                    continue
                    
                video_path = video_dir / "1080p60" / filename
                if video_path.exists():
                    return video_path, video_dir
            return None, None

        # Execute search in thread pool
        found_file, parent_tmp_dir = await asyncio.get_event_loop().run_in_executor(
            THREAD_POOL,
            search_video_sync
        )
        
        if not found_file:
            raise HTTPException(status_code=404, detail=f"Video file not found")
        
        # Delete the directory
        if parent_tmp_dir and parent_tmp_dir.exists():
            await asyncio.get_event_loop().run_in_executor(
                THREAD_POOL,
                shutil.rmtree,
                str(parent_tmp_dir)
            )
            return {"success": True, "message": f"Successfully deleted video"}
            
    except Exception as e:
        logger.error(f"Error during video deletion: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error deleting video: {str(e)}")

# Helper function to construct Manim prompt
def construct_manim_prompt(params: InputParams, visualization_name: str) -> str:
    return f'''#Persona: You are a Manim python code generator. Generate python code only, no other text.

Generate manim visualization for: {params.query}
Visualization name: {visualization_name}

# Requirements:
- *Valid manim python code only*
- Scene/class name must be "Scene" 
- Provide solution if topic is a question
- Create logical solution for math/STEM questions
- Provide step by step solution for Math / Physics question
- Make sure to draw within the canvas of resolution {params.resolution}
- Don't overlap elements in a chaotic manner, make sure the video is viewable and clean.
- Use {params.theme} theme and {params.accent_color} accent color
- HD video. resolution: {params.resolution}
- Clean, uncramped visualization
- Use arrows/graphs as needed

# Output Format:
```python {params.resolution}
{{PYTHON_CODE}}
```
'''