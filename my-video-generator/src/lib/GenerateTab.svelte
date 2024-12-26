<script>
  import { fade } from 'svelte/transition';
  import { Sparkles, Video, Wand2 } from 'lucide-svelte';
  import { onDestroy } from 'svelte';

  let query = '';
  let name = '';
  let theme = 'Dark';
  let accentColor = 'Blue';
  let resolution = '1920x1080';
  let specialInstructions = '';
  let isLoading = false;
  let showSuccess = false;
  let jobStatus = null;
  let errorMessage = '';
  
  const themes = ['Dark', 'Light', 'Neon', 'Minimal'];
  const accentColors = ['Blue', 'Purple', 'Green', 'Red', 'Orange'];
  const resolutions = ['1920x1080', '920x1080', '1080x1920', '1280x720'];

  let statusCheckInterval;

  onDestroy(() => {
    if (statusCheckInterval) {
      clearInterval(statusCheckInterval);
    }
  });

  async function checkJobStatus(jobId) {
    try {
      const response = await fetch(`/api/job/${jobId}`);
      const data = await response.json();
      
      if (data.status === 'completed') {
        clearInterval(statusCheckInterval);
        isLoading = false;
        showSuccess = true;
        setTimeout(() => {
          showSuccess = false;
        }, 3000);
      } else if (data.status === 'failed') {
        clearInterval(statusCheckInterval);
        isLoading = false;
        errorMessage = data.error || 'Generation failed';
        setTimeout(() => {
          errorMessage = '';
        }, 5000);
      }
      
      jobStatus = data.status;
    } catch (error) {
      console.error('Error checking job status:', error);
      clearInterval(statusCheckInterval);
      isLoading = false;
      errorMessage = 'Error checking job status';
    }
  }

  async function handleSubmit() {
    if (!query.trim()) {
      errorMessage = 'Please enter a description for your video';
      return;
    }

    isLoading = true;
    showSuccess = false;
    errorMessage = '';
    
    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: {
          'accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          name: name || query.slice(0, 50),
          theme,
          accent_color: accentColor,
          resolution,
          special_instructions: specialInstructions || "",
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to start generation');
      }

      const data = await response.json();
      
      if (data.job_id) {
        // Start polling for job status
        if (statusCheckInterval) {
          clearInterval(statusCheckInterval);
        }
        statusCheckInterval = setInterval(() => checkJobStatus(data.job_id), 2000);
      } else {
        throw new Error('No job ID received');
      }
    } catch (error) {
      console.error('Error:', error);
      isLoading = false;
      errorMessage = error.message;
      setTimeout(() => {
        errorMessage = '';
      }, 5000);
    }
  }
</script>

<div class="min-h-screen space-y-8">
  <!-- Animated Title Section -->
  <div class="text-center space-y-4 mb-12">
    <div class="flex items-center justify-center space-x-3">
      <Video class="w-8 h-8 text-blue-400" />
      <h1 class="text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 animate-pulse">
        Create!
      </h1>
      <Sparkles class="w-8 h-8 text-purple-400" />
    </div>
    <p class="text-gray-400 text-lg">Transform your ideas into stunning videos with AI</p>
  </div>

  <!-- Status Messages -->
  {#if showSuccess}
    <div class="fixed top-4 right-4 bg-green-500/20 border-green-500/50 text-green-200 p-4 rounded-lg" transition:fade>
      <div class="flex items-center space-x-2">
        <Wand2 class="w-4 h-4" />
        <span>Video generated successfully!</span>
      </div>
    </div>
  {/if}

  {#if errorMessage}
    <div class="fixed top-4 right-4 bg-red-500/20 border-red-500/50 text-red-200 p-4 rounded-lg" transition:fade>
      <div class="flex items-center space-x-2">
        <span class="text-red-200">{errorMessage}</span>
      </div>
    </div>
  {/if}

  <!-- Job Status -->
  {#if jobStatus && jobStatus !== 'completed' && !errorMessage}
    <div class="fixed top-4 right-4 bg-blue-500/20 border-blue-500/50 text-blue-200 p-4 rounded-lg" transition:fade>
      <div class="flex items-center space-x-2">
        <div class="animate-spin h-4 w-4 border-2 border-blue-500 rounded-full border-t-transparent"></div>
        <span>Status: {jobStatus}</span>
      </div>
    </div>
  {/if}

  <!-- Video Description Input -->
  <div class="bg-white/5 backdrop-blur-xl p-8 rounded-2xl border border-white/10 shadow-2xl">
    <label class="block text-sm font-medium text-gray-300">
      Video Description
      <textarea
        bind:value={query}
        class="mt-1 w-full bg-gray-800/50 border border-gray-700 rounded-xl p-3 text-gray-100 h-48 resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all placeholder-gray-500"
        placeholder="Describe your video idea..."
      ></textarea>
    </label>
  </div>

  <!-- Settings Grid -->
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
    <!-- Left Column -->
    <div class="space-y-6 bg-white/5 backdrop-blur-xl p-8 rounded-2xl border border-white/10 shadow-2xl">
      <div class="space-y-4">
        <label class="block text-sm font-medium text-gray-300">
          Project Name
          <input
            type="text"
            bind:value={name}
            class="mt-1 w-full bg-gray-800/50 border border-gray-700 rounded-xl p-3 text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all placeholder-gray-500"
            placeholder="Enter project name..."
          />
        </label>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-300">
            Theme
            <select
              bind:value={theme}
              class="mt-1 w-full bg-gray-800/50 border border-gray-700 rounded-xl p-3 text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            >
              {#each themes as t}
                <option value={t}>{t}</option>
              {/each}
            </select>
          </label>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-300">
            Accent Color
            <select
              bind:value={accentColor}
              class="mt-1 w-full bg-gray-800/50 border border-gray-700 rounded-xl p-3 text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            >
              {#each accentColors as color}
                <option value={color}>{color}</option>
              {/each}
            </select>
          </label>
        </div>
      </div>
    </div>

    <!-- Right Column -->
    <div class="space-y-6 bg-white/5 backdrop-blur-xl p-8 rounded-2xl border border-white/10 shadow-2xl">
      <div>
        <label class="block text-sm font-medium text-gray-300">
          Resolution
          <select
            bind:value={resolution}
            class="mt-1 w-full bg-gray-800/50 border border-gray-700 rounded-xl p-3 text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
          >
            {#each resolutions as res}
              <option value={res}>{res}</option>
            {/each}
          </select>
        </label>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-300">
          Special Instructions
          <textarea
            bind:value={specialInstructions}
            class="mt-1 w-full bg-gray-800/50 border border-gray-700 rounded-xl p-3 text-gray-100 h-32 resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all placeholder-gray-500"
            placeholder="Add any special instructions..."
          ></textarea>
        </label>
      </div>
    </div>
  </div>

  <!-- Generate Button -->
  <button
    type="button"
    on:click={handleSubmit}
    disabled={isLoading || !query}
    class="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 disabled:from-gray-600 disabled:to-gray-700 text-white font-medium py-4 px-6 rounded-xl transition-all duration-200 transform hover:scale-[1.02] disabled:hover:scale-100 disabled:cursor-not-allowed shadow-lg"
  >
    {#if isLoading}
      <span class="flex items-center justify-center">
        <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
        Creating Magic...
      </span>
    {:else}
      <span class="flex items-center justify-center">
        <Wand2 class="mr-2" />
        Generate Video
      </span>
    {/if}
  </button>
</div>