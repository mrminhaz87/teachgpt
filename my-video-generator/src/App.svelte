<script>
  import { onMount } from 'svelte';
  import VideoGallery from './lib/VideoGallery.svelte';
  import GenerateTab from './lib/GenerateTab.svelte';
  import { fade, slide } from 'svelte/transition';
  import { Video } from 'lucide-svelte';

  let activeTab = 'generate';
  
  onMount(() => {
    // Force dark mode
    const url = new URL(window.location);
    if (url.searchParams.get('theme') !== 'dark') {
      url.searchParams.set('theme', 'dark');
      window.location.href = url.href;
    }
  });
</script>

<main class="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black">
  <div class="min-h-screen backdrop-blur-xl bg-black/30">
    <!-- Modern Navigation -->
    <nav class="sticky top-0 z-50 bg-gradient-to-b from-black/80 to-black/40 backdrop-blur-xl border-b border-white/5">
      <div class="max-w-7xl mx-auto px-4">
        <div class="flex flex-col py-6">
          <!-- Logo and Brand Section -->
          <div class="flex items-center justify-between mb-6">
            <div class="flex items-center space-x-3">
              <div class="relative group cursor-pointer">
                <div class="absolute -inset-2 rounded-lg bg-gradient-to-r from-blue-600/20 to-purple-600/20 blur-lg group-hover:opacity-100 opacity-75 transition duration-200"></div>
                <div class="relative flex items-center space-x-2 bg-black/20 rounded-xl px-4 py-2 border border-white/5">
                  <Video class="w-5 h-5 text-blue-400" />
                  <span class="text-lg font-semibold bg-gradient-to-r from-blue-400 to-purple-500 text-transparent bg-clip-text">
                    TeachGPT
                  </span>
                </div>
              </div>
            </div>
            
            <!-- Stats or Additional Info -->
            <div class="flex items-center space-x-6 text-sm">
              <div class="flex items-center space-x-2">
                <div class="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span class="text-gray-400">AI Ready</span>
              </div>
              <div class="flex items-center space-x-2">
                <div class="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                <span class="text-gray-400">Ultra Fast</span>
              </div>
            </div>
          </div>

          <!-- Modern Tab Navigation -->
          <div class="flex items-center justify-center">
            <div class="flex space-x-1 bg-white/5 rounded-lg p-1">
              <button
                class="relative px-8 py-2 rounded-lg transition-all duration-300 {activeTab === 'generate' ? 'text-white' : 'text-gray-400 hover:text-white'}"
                on:click={() => activeTab = 'generate'}
              >
                {#if activeTab === 'generate'}
                  <div class="absolute inset-0 bg-gradient-to-r from-blue-500/90 to-purple-500/90 rounded-lg"></div>
                {/if}
                <div class="relative flex items-center justify-center space-x-2">
                  <span class="text-sm font-medium">Generate</span>
                </div>
              </button>
              
              <button
                class="relative px-8 py-2 rounded-lg transition-all duration-300 {activeTab === 'gallery' ? 'text-white' : 'text-gray-400 hover:text-white'}"
                on:click={() => activeTab = 'gallery'}
              >
                {#if activeTab === 'gallery'}
                  <div class="absolute inset-0 bg-gradient-to-r from-blue-500/90 to-purple-500/90 rounded-lg"></div>
                {/if}
                <div class="relative flex items-center justify-center space-x-2">
                  <span class="text-sm font-medium">Gallery</span>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content Area -->
    <div class="max-w-7xl mx-auto p-6">
      {#if activeTab === 'generate'}
        <div in:slide>
          <GenerateTab />
        </div>
      {:else}
        <div in:slide>
          <VideoGallery />
        </div>
      {/if}
    </div>
  </div>
</main>

<style>
  :global(body) {
    background-color: #111827;
    margin: 0;
    font-family: 'Inter', sans-serif;
  }
</style>