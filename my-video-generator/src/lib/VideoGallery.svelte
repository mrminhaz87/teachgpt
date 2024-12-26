<script>
  import { onMount } from 'svelte';
  import { fade, scale, fly } from 'svelte/transition';

  const videoModules = import.meta.glob('/public/movie/**/*.mp4', { eager: true });

  let videos = [];
  let selectedVideo = null;
  let loading = true;
  let deletingVideo = null;
  let deleteError = null;
  let showDeleteConfirm = null;
  let modalRef;
  let previousActiveElement;

  onMount(() => {
    loadVideos();
  });

  function loadVideos() {
    videos = Object.keys(videoModules)
      .filter(path => {
        const filename = path.split('/').pop();
        return !filename.startsWith('uncached');
      })
      .map(path => {
        const title = path.split('/').pop().replace('.mp4', '');
        const url = path.replace('/public', '');
        
        return {
          url,
          title,
          filename: path.split('/').pop(),
          thumbnail: `${url}#t=0.1`
        };
      });

    loading = false;
  }

  function handleModalOpen() {
    previousActiveElement = document.activeElement;
    setTimeout(() => {
      if (modalRef) {
        const focusableElements = modalRef.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        if (focusableElements.length) {
          focusableElements[0].focus();
        }
      }
    }, 0);
  }

  function handleModalClose() {
    if (previousActiveElement) {
      previousActiveElement.focus();
    }
  }

  function confirmDelete(video) {
    showDeleteConfirm = video;
  }

  async function deleteVideo(video) {
    try {
      deletingVideo = video;
      deleteError = null;
      showDeleteConfirm = null;
      
      const response = await fetch(`/api/video/${encodeURIComponent(video.filename)}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to delete video');
      }

      videos = videos.filter(v => v.filename !== video.filename);
      
      if (selectedVideo?.filename === video.filename) {
        selectedVideo = null;
      }
    } catch (error) {
      deleteError = error.message;
    } finally {
      deletingVideo = null;
    }
  }

  function handleVideoClick(video) {
    selectedVideo = video;
    handleModalOpen();
  }

  function handleKeyDown(event, video) {
    if (event.key === 'Enter' || event.key === ' ') {
      handleVideoClick(video);
    }
  }

  function closeModal() {
    handleModalClose();
    selectedVideo = null;
  }
</script>

<div class="min-h-[80vh] space-y-8">
  {#if loading}
    <div class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500"></div>
    </div>
  {:else if videos.length === 0}
    <div class="text-center py-12 bg-black/20 rounded-xl backdrop-blur-lg border border-gray-800/50">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z" />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-300">No videos found</h3>
    </div>
  {:else}
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {#each videos as video}
        <div
          class="group relative bg-black/20 rounded-xl overflow-hidden transform hover:scale-105 transition-all duration-200 backdrop-blur-lg border border-gray-800/50"
          in:scale={{ duration: 200 }}
        >
          <button
            type="button"
            class="w-full text-left"
            on:click={() => handleVideoClick(video)}
            on:keydown={(e) => handleKeyDown(e, video)}
            aria-label="Open video: {video.title}"
          >
            <div class="aspect-w-16 aspect-h-9">
              <video
                src={video.thumbnail}
                class="w-full object-cover"
                preload="metadata"
              >
                <track kind="captions" />
              </video>
              <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-200"></div>
            </div>
            <div class="p-4">
              <h3 class="text-lg font-medium text-gray-100 truncate group-hover:text-blue-400 transition-colors">
                {video.title}
              </h3>
            </div>
          </button>
          <button
            type="button"
            class="absolute top-2 right-2 p-2 bg-red-500/80 hover:bg-red-600 rounded-full text-white opacity-0 group-hover:opacity-100 transition-all duration-200 transform hover:scale-110"
            on:click={() => confirmDelete(video)}
            aria-label="Delete video"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      {/each}
    </div>
  {/if}

  {#if selectedVideo}
    <div 
      class="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50" 
      transition:fade={{ duration: 200 }}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      on:click={closeModal}
      on:keydown={(e) => e.key === 'Escape' && closeModal()}
      bind:this={modalRef}
    >
      <div 
        class="bg-gray-900/90 p-6 rounded-xl max-w-4xl w-full mx-4 border border-gray-800/50" 
        transition:scale={{ duration: 200 }}
        on:click|stopPropagation
        role="document"
      >
        <div class="aspect-w-16 aspect-h-9 bg-black rounded-lg overflow-hidden">
          <video
            src={selectedVideo.url}
            controls
            autoplay
            class="w-full"
          >
            <track kind="captions" />
          </video>
        </div>
        <div class="mt-4 flex justify-between items-center">
          <h3 id="modal-title" class="text-xl font-medium text-gray-100">{selectedVideo.title}</h3>
          <div class="flex items-center space-x-3">
            <button
              type="button"
              class="px-4 py-2 bg-red-500 hover:bg-red-600 rounded-lg text-white transition-colors flex items-center space-x-2"
              on:click={() => confirmDelete(selectedVideo)}
              disabled={deletingVideo === selectedVideo}
            >
              {#if deletingVideo === selectedVideo}
                <div class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Deleting...</span>
              {:else}
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                <span>Delete</span>
              {/if}
            </button>
            <button
              type="button"
              class="px-4 py-2 bg-blue-500 hover:bg-blue-600 rounded-lg text-white transition-colors flex items-center space-x-2"
              on:click={closeModal}
              aria-label="Close video"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
              <span>Close</span>
            </button>
          </div>
        </div>
        {#if deleteError}
          <div 
            class="mt-4 p-4 bg-red-500/20 border border-red-500/50 rounded-lg text-red-200"
            transition:fly={{ y: 20, duration: 200 }}
          >
            Error: {deleteError}
          </div>
        {/if}
      </div>
    </div>
  {/if}

  {#if showDeleteConfirm}
    <div 
      class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-end sm:items-center justify-center z-50 p-4" 
      transition:fade={{ duration: 200 }}
      role="dialog"
      aria-modal="true"
      on:click={() => showDeleteConfirm = null}
      on:keydown={(e) => e.key === 'Escape' && (showDeleteConfirm = null)}
      tabindex="0"
    >
      <div 
        class="bg-gray-900/90 w-full max-w-lg rounded-2xl border border-gray-800/50 overflow-hidden"
        transition:fly={{ y: 50, duration: 300 }}
        on:click|stopPropagation
        role="document"
      >
        <div class="p-6">
          <div class="flex items-center space-x-3">
            <div class="flex-shrink-0 w-12 h-12 rounded-full bg-red-500/20 flex items-center justify-center">
              <svg class="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div>
              <h3 class="text-lg font-medium text-gray-100">Delete video?</h3>
              <p class="mt-1 text-sm text-gray-400">
                Are you sure you want to delete "{showDeleteConfirm.title}"? This action cannot be undone.
              </p>
            </div>
          </div>
        </div>
        <div class="px-6 py-4 bg-gray-800/50 flex justify-end space-x-3">
          <button
            type="button"
            class="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-gray-200 transition-colors"
            on:click={() => showDeleteConfirm = null}
          >
            Cancel
          </button>
          <button
            type="button"
            class="px-4 py-2 bg-red-500 hover:bg-red-600 rounded-lg text-white transition-colors flex items-center space-x-2"
            on:click={() => deleteVideo(showDeleteConfirm)}
            disabled={deletingVideo}
          >
            {#if deletingVideo}
              <div class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Deleting...</span>
            {:else}
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              <span>Delete</span>
            {/if}
          </button>
        </div>
      </div>
    </div>
  {/if}
</div>