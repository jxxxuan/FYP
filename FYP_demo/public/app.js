// App State
let allVideos = [];
let filteredVideos = [];
let currentVideoIndex = -1;

// Custom Video Player Reference
const videoPlayer = document.getElementById('mainVideo');
const videoWrapper = document.getElementById('videoWrapper');
const playPauseBtn = document.getElementById('playPauseBtn');
const playIcon = document.getElementById('playIcon');
const pauseIcon = document.getElementById('pauseIcon');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const currentTimeEl = document.getElementById('currentTime');
const durationTimeEl = document.getElementById('durationTime');
const progressContainer = document.getElementById('progressContainer');
const progressBarActive = document.getElementById('progressBarActive');
const bufferBar = document.getElementById('bufferBar');
const progressScrubber = document.getElementById('progressScrubber');
const progressTooltip = document.getElementById('progressTooltip');
const muteBtn = document.getElementById('muteBtn');
const volumeHighIcon = document.getElementById('volumeHighIcon');
const volumeMutedIcon = document.getElementById('volumeMutedIcon');
const volumeSlider = document.getElementById('volumeSlider');
const speedBtn = document.getElementById('speedBtn');
const speedDisplay = document.getElementById('speedDisplay');
const speedMenu = document.getElementById('speedMenu');
const fullscreenBtn = document.getElementById('fullscreenBtn');
const fullscreenEnter = document.getElementById('fullscreenEnter');
const fullscreenExit = document.getElementById('fullscreenExit');
const videoSpinner = document.getElementById('videoSpinner');
const overlayPlayBtn = document.getElementById('overlayPlayBtn');

// DOM Elements
const videoListEl = document.getElementById('videoList');
const videoCountEl = document.getElementById('videoCount');
const noVideoStateEl = document.getElementById('noVideoState');
const activePlayerStateEl = document.getElementById('activePlayerState');

// Video Metadata Elements
const playerVideoTitle = document.getElementById('playerVideoTitle');
const playerVideoTags = document.getElementById('playerVideoTags');

// Fallback static video list for file:// protocol
const FALLBACK_VIDEOS = [
  { filename: 'ep108199_22-00-09.mp4', size: 1919759, mtime: '2026-06-25T13:35:26.089Z' },
  { filename: 'ep108299_22-00-14.mp4', size: 583750,  mtime: '2026-06-25T13:35:26.024Z' },
  { filename: 'ep108599_22-00-25.mp4', size: 466421,  mtime: '2026-06-25T13:35:25.895Z' },
  { filename: 'ep108699_22-00-27.mp4', size: 628183,  mtime: '2026-06-25T13:35:26.114Z' },
  { filename: 'ep108699_22-00-28.mp4', size: 546584,  mtime: '2026-06-25T13:35:25.918Z' },
  { filename: 'ep108699_22-00-30.mp4', size: 774377,  mtime: '2026-06-25T13:35:25.840Z' },
  { filename: 'ep108999_22-00-38.mp4', size: 635422,  mtime: '2026-06-25T13:35:25.874Z' },
  { filename: 'ep108999_22-00-39.mp4', size: 518597,  mtime: '2026-06-25T13:35:26.045Z' },
  { filename: 'ep109699_22-01-03.mp4', size: 4672221, mtime: '2026-06-25T13:35:26.000Z' }
];

// Init
document.addEventListener('DOMContentLoaded', () => {
  // Show protocol warning if loaded via file://
  if (window.location.protocol === 'file:') {
    const warningEl = document.getElementById('protocolWarning');
    if (warningEl) warningEl.style.display = 'flex';
  }
  fetchVideos();
  initPlayerControls();
});

// Helper: Format File Size
function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Helper: Format Time (seconds to MM:SS)
function formatTime(seconds) {
  if (isNaN(seconds) || seconds === Infinity) return '00:00';
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);
  
  if (hrs > 0) {
    return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

// Helper: Parse Filename metadata
function parseFilename(filename) {
  // Pattern 1: debug_Town04_ep108199_22-00-09.mp4
  const regexDebug = /debug_([^_]+)_ep(\d+)_([\d-]+)/;
  const matchDebug = filename.match(regexDebug);
  if (matchDebug) {
    return {
      town: matchDebug[1],
      episode: matchDebug[2],
      time: matchDebug[3].replace(/-/g, ':')
    };
  }

  // Pattern 2: ep108199_22-00-09.mp4
  const regexSimple = /ep(\d+)_([\d-]+)/;
  const matchSimple = filename.match(regexSimple);
  if (matchSimple) {
    return {
      town: 'Town04', // Fallback scene
      episode: matchSimple[1],
      time: matchSimple[2].replace(/-/g, ':')
    };
  }

  return {
    town: 'Demo Town',
    episode: 'N/A',
    time: 'N/A'
  };
}

// Fetch Videos
async function fetchVideos() {
  // Check if running on local file system (file://)
  if (window.location.protocol === 'file:') {
    console.warn('Running in file protocol mode. Using local fallback video list.');
    allVideos = FALLBACK_VIDEOS.map(v => ({
      ...v,
      url: `../demo_video/${v.filename}`
    }));
    filteredVideos = [...allVideos];
    applySortAndRender();
    return;
  }

  try {
    const response = await fetch('videos.json');
    const data = await response.json();
    if (data.success && data.videos) {
      allVideos = data.videos;
      filteredVideos = [...allVideos];
      applySortAndRender();
    } else {
      showErrorState();
    }
  } catch (error) {
    console.error('Error fetching videos:', error);
    showErrorState();
  }
}

// Show Error
function showErrorState() {
  videoListEl.innerHTML = '<div class="no-results">❌ Failed to retrieve video list. Please check the backend server.</div>';
}

// Apply Sorting and Render List
function applySortAndRender() {
  // Sort alphabetically by filename by default
  filteredVideos.sort((a, b) => a.filename.localeCompare(b.filename));
  renderVideoList(filteredVideos);
}

// Render Video Sidebar List
function renderVideoList(videos) {
  videoCountEl.textContent = videos.length;
  
  if (videos.length === 0) {
    videoListEl.innerHTML = '<div class="no-results">🔍 No matching videos found</div>';
    return;
  }

  videoListEl.innerHTML = '';
  videos.forEach((video, index) => {
    const meta = parseFilename(video.filename);
    const item = document.createElement('div');
    item.className = `video-item ${index === currentVideoIndex ? 'active' : ''}`;
    item.dataset.index = index;
    
    // Check if currently playing this exact video object
    const isPlayingCurrent = currentVideoIndex >= 0 && 
                             allVideos[currentVideoIndex]?.filename === video.filename;
    if (isPlayingCurrent) {
      item.classList.add('active');
    }

    item.innerHTML = `
      <div class="item-title" title="${video.filename}">${video.filename}</div>
      <div class="item-tags">
        <span class="badge badge-episode">Ep ${meta.episode}</span>
      </div>
    `;

    item.addEventListener('click', () => {
      selectVideo(video, index);
    });

    videoListEl.appendChild(item);
  });
}

// Select Video
function selectVideo(video, filteredIndex) {
  // Save global state
  currentVideoIndex = filteredIndex;
  
  // Update sidebar active classes
  const items = videoListEl.querySelectorAll('.video-item');
  items.forEach((item, idx) => {
    if (idx === filteredIndex) {
      item.classList.add('active');
    } else {
      item.classList.remove('active');
    }
  });

  // Switch View Container
  noVideoStateEl.style.display = 'none';
  activePlayerStateEl.style.display = 'flex';

  // Clear any existing error state
  const errorOverlay = document.getElementById('videoErrorOverlay');
  if (errorOverlay) errorOverlay.style.display = 'none';

  // Load Video source
  videoPlayer.src = video.url;
  videoPlayer.load();
  videoSpinner.style.display = 'none';

  // Reset custom player controls UI
  progressBarActive.style.width = '0%';
  bufferBar.style.width = '0%';
  currentTimeEl.textContent = '00:00';
  durationTimeEl.textContent = '00:00';
  playIcon.style.display = 'block';
  pauseIcon.style.display = 'none';
  
  // Set speed back to 1.0x
  videoPlayer.playbackRate = 1.0;
  speedDisplay.textContent = '1.0x';
  const speedOptions = speedMenu.querySelectorAll('.speed-option');
  speedOptions.forEach(opt => {
    if (opt.dataset.speed === '1.0' || opt.dataset.speed === '1') {
      opt.classList.add('active');
    } else {
      opt.classList.remove('active');
    }
  });

  // Populate metadata
  const meta = parseFilename(video.filename);
  playerVideoTitle.textContent = video.filename.replace('.mp4', '');
  
  playerVideoTags.innerHTML = `
    <span class="badge badge-episode">Episode ${meta.episode}</span>
  `;



  // Auto Play
  videoPlayer.play().catch(e => {
    console.log('Autoplay blocked. User gesture required.', e);
  });
}


// Custom Player Controls Setup
function initPlayerControls() {
  // Play / Pause toggling
  function togglePlay() {
    if (videoPlayer.paused) {
      videoPlayer.play();
    } else {
      videoPlayer.pause();
    }
  }

  playPauseBtn.addEventListener('click', togglePlay);
  overlayPlayBtn.addEventListener('click', togglePlay);
  videoPlayer.addEventListener('click', togglePlay);

  videoPlayer.addEventListener('play', () => {
    playIcon.style.display = 'none';
    pauseIcon.style.display = 'block';
    overlayPlayBtn.style.opacity = 0;
    overlayPlayBtn.style.visibility = 'hidden';
  });

  videoPlayer.addEventListener('pause', () => {
    playIcon.style.display = 'block';
    pauseIcon.style.display = 'none';
    overlayPlayBtn.style.opacity = 1;
    overlayPlayBtn.style.visibility = 'visible';
  });

  // Previous & Next navigation
  prevBtn.addEventListener('click', () => {
    if (filteredVideos.length === 0) return;
    let prevIndex = currentVideoIndex - 1;
    if (prevIndex < 0) prevIndex = filteredVideos.length - 1;
    selectVideo(filteredVideos[prevIndex], prevIndex);
  });

  nextBtn.addEventListener('click', () => {
    if (filteredVideos.length === 0) return;
    let nextIndex = currentVideoIndex + 1;
    if (nextIndex >= filteredVideos.length) nextIndex = 0;
    selectVideo(filteredVideos[nextIndex], nextIndex);
  });

  // Buffer and progress update
  videoPlayer.addEventListener('timeupdate', () => {
    const cur = videoPlayer.currentTime;
    const dur = videoPlayer.duration;
    currentTimeEl.textContent = formatTime(cur);
    
    if (dur) {
      const pct = (cur / dur) * 100;
      progressBarActive.style.width = `${pct}%`;
    }
  });

  videoPlayer.addEventListener('progress', () => {
    const dur = videoPlayer.duration;
    if (dur && videoPlayer.buffered.length > 0) {
      const bufferedEnd = videoPlayer.buffered.end(videoPlayer.buffered.length - 1);
      const pct = (bufferedEnd / dur) * 100;
      bufferBar.style.width = `${pct}%`;
    }
  });

  videoPlayer.addEventListener('loadedmetadata', () => {
    durationTimeEl.textContent = formatTime(videoPlayer.duration);
  });

  // Scrubber seeking
  let isDraggingProgress = false;

  function seek(e) {
    const rect = progressContainer.getBoundingClientRect();
    const pos = (e.clientX - rect.left) / rect.width;
    const targetTime = Math.max(0, Math.min(1, pos)) * videoPlayer.duration;
    if (!isNaN(targetTime)) {
      videoPlayer.currentTime = targetTime;
    }
  }

  progressContainer.addEventListener('mousedown', (e) => {
    isDraggingProgress = true;
    seek(e);
  });

  window.addEventListener('mousemove', (e) => {
    if (isDraggingProgress) {
      seek(e);
    }
  });

  window.addEventListener('mouseup', () => {
    isDraggingProgress = false;
  });

  // Tooltip on Hover
  progressContainer.addEventListener('mousemove', (e) => {
    const rect = progressContainer.getBoundingClientRect();
    const pos = (e.clientX - rect.left) / rect.width;
    const targetTime = Math.max(0, Math.min(1, pos)) * videoPlayer.duration;
    
    if (!isNaN(targetTime)) {
      progressTooltip.textContent = formatTime(targetTime);
      progressTooltip.style.left = `${(e.clientX - rect.left)}px`;
    }
  });

  // Volume
  volumeSlider.addEventListener('input', (e) => {
    const vol = parseFloat(e.target.value);
    videoPlayer.volume = vol;
    videoPlayer.muted = (vol === 0);
    updateVolumeIcon(vol, videoPlayer.muted);
  });

  muteBtn.addEventListener('click', () => {
    videoPlayer.muted = !videoPlayer.muted;
    if (videoPlayer.muted) {
      updateVolumeIcon(0, true);
    } else {
      updateVolumeIcon(videoPlayer.volume, false);
      volumeSlider.value = videoPlayer.volume;
    }
  });

  function updateVolumeIcon(vol, isMuted) {
    if (isMuted || vol === 0) {
      volumeHighIcon.style.display = 'none';
      volumeMutedIcon.style.display = 'block';
    } else {
      volumeHighIcon.style.display = 'block';
      volumeMutedIcon.style.display = 'none';
    }
  }

  // Playback Speed
  speedBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    speedMenu.classList.toggle('show');
  });

  document.addEventListener('click', () => {
    speedMenu.classList.remove('show');
  });

  const speedOptions = speedMenu.querySelectorAll('.speed-option');
  speedOptions.forEach(opt => {
    opt.addEventListener('click', (e) => {
      const speed = parseFloat(opt.dataset.speed);
      videoPlayer.playbackRate = speed;
      speedDisplay.textContent = opt.textContent.includes('正常') ? '1.0x' : `${speed}x`;
      
      speedOptions.forEach(o => o.classList.remove('active'));
      opt.classList.add('active');
    });
  });

  // Fullscreen
  function toggleFullscreen() {
    if (!document.fullscreenElement) {
      videoWrapper.requestFullscreen().catch(err => {
        console.error(`Error attempting to enable full-screen: ${err.message}`);
      });
    } else {
      document.exitFullscreen();
    }
  }

  fullscreenBtn.addEventListener('click', toggleFullscreen);

  document.addEventListener('fullscreenchange', () => {
    if (document.fullscreenElement) {
      fullscreenEnter.style.display = 'none';
      fullscreenExit.style.display = 'block';
    } else {
      fullscreenEnter.style.display = 'block';
      fullscreenExit.style.display = 'none';
    }
  });

  // Spinner states (Waiting/Buffering indicator)
  videoPlayer.addEventListener('waiting', () => {
    if (!videoPlayer.paused) {
      videoSpinner.style.display = 'flex';
    }
  });

  videoPlayer.addEventListener('playing', () => {
    videoSpinner.style.display = 'none';
  });

  videoPlayer.addEventListener('pause', () => {
    videoSpinner.style.display = 'none';
  });

  videoPlayer.addEventListener('seeked', () => {
    videoSpinner.style.display = 'none';
  });

  videoPlayer.addEventListener('seeking', () => {
    if (!videoPlayer.paused) {
      videoSpinner.style.display = 'flex';
    }
  });

  videoPlayer.addEventListener('canplay', () => {
    videoSpinner.style.display = 'none';
  });

  // Error handling
  videoPlayer.addEventListener('error', () => {
    const err = videoPlayer.error;
    let message = 'Unknown media error';
    if (err) {
      switch (err.code) {
        case 1: message = 'Video playback aborted'; break;
        case 2: message = 'Network error, video download failed'; break;
        case 3: message = 'Video decoding failed. File may be corrupted or codec incompatible.'; break;
        case 4: message = 'Browser does not support this video format or codec (e.g., H.265/HEVC)'; break;
      }
    }
    console.error('Video Error:', err, message);
    
    let errorOverlay = document.getElementById('videoErrorOverlay');
    if (!errorOverlay) {
      errorOverlay = document.createElement('div');
      errorOverlay.id = 'videoErrorOverlay';
      errorOverlay.className = 'video-error-overlay';
      videoWrapper.appendChild(errorOverlay);
    }
    errorOverlay.innerHTML = `
      <div class="error-msg-content">
        <span class="error-icon" style="font-size: 32px;">❌</span>
        <h4 style="font-size: 18px; font-weight: 700; margin: 10px 0 6px; color: #f8fafc;">Playback Failed</h4>
        <p style="font-size: 14px; color: #94a3b8; margin-bottom: 12px;">${message}</p>
        <small style="font-family: monospace; font-size: 11px; color: #64748b; word-break: break-all;">${videoPlayer.src}</small>
      </div>
    `;
    errorOverlay.style.display = 'flex';
    videoSpinner.style.display = 'none';
  });

  // Keyboard Hotkeys
  window.addEventListener('keydown', (e) => {
    
    // Space: Play/Pause
    if (e.key === ' ' || e.code === 'Space') {
      e.preventDefault(); // Prevent page scrolling
      togglePlay();
    }
    
    // M: Mute/Unmute
    if (e.key === 'm' || e.key === 'M') {
      muteBtn.click();
    }
    
    // F: Fullscreen toggle
    if (e.key === 'f' || e.key === 'F') {
      toggleFullscreen();
    }

    // Left/Right: Seek 5s back/forward
    if (e.key === 'ArrowLeft') {
      videoPlayer.currentTime = Math.max(0, videoPlayer.currentTime - 5);
    }
    if (e.key === 'ArrowRight') {
      videoPlayer.currentTime = Math.min(videoPlayer.duration || 0, videoPlayer.currentTime + 5);
    }
  });
}
