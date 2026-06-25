const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;

const VIDEO_DIR = path.join(__dirname, 'demo_video');
const PUBLIC_DIR = path.join(__dirname, 'public');

// Request logger middleware
app.use((req, res, next) => {
  console.log(`[${new Date().toLocaleTimeString()}] ${req.method} ${req.url}`);
  next();
});

// Ensure video directory exists
if (!fs.existsSync(VIDEO_DIR)) {
  fs.mkdirSync(VIDEO_DIR, { recursive: true });
}

// Serve frontend assets
app.use(express.static(PUBLIC_DIR));

// Serve videos statically with support for range requests (streaming)
app.use('/demo_video', express.static(VIDEO_DIR));

// API: Get video list
app.get('/api/videos', async (req, res) => {
  try {
    const files = await fs.promises.readdir(VIDEO_DIR);
    const videoFiles = files.filter(file => {
      const ext = path.extname(file).toLowerCase();
      return ext === '.mp4' || ext === '.webm' || ext === '.ogg';
    });

    const videos = await Promise.all(
      videoFiles.map(async (filename) => {
        const filePath = path.join(VIDEO_DIR, filename);
        const stats = await fs.promises.stat(filePath);
        return {
          filename,
          url: `/demo_video/${encodeURIComponent(filename)}`,
          size: stats.size,
          mtime: stats.mtime,
          createdAt: stats.birthtime
        };
      })
    );

    // Sort videos by filename/date (newest first or alphabetic default)
    videos.sort((a, b) => b.mtime - a.mtime);

    res.json({ success: true, videos });
  } catch (error) {
    console.error('Error reading video directory:', error);
    res.status(500).json({ success: false, error: 'Failed to read video directory' });
  }
});

// Fallback to index.html for single page app routing
app.get('*', (req, res) => {
  res.sendFile(path.join(PUBLIC_DIR, 'index.html'));
});

app.listen(PORT, () => {
  console.log(`=================================================`);
  console.log(`🚀 Video Demo App is running at:`);
  console.log(`   👉 http://localhost:${PORT}`);
  console.log(`=================================================`);
});
