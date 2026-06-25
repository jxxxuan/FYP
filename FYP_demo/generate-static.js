const fs = require('fs');
const path = require('path');

const projectRoot = __dirname;
const publicDir = path.join(projectRoot, 'public');
const oldVideoDir = path.join(projectRoot, 'demo_video');
const newVideoDir = path.join(publicDir, 'demo_video');

// 1. Move demo_video into public/ if not already done
if (fs.existsSync(oldVideoDir) && !fs.existsSync(newVideoDir)) {
  console.log('📁 Moving demo_video directory inside public/ for static hosting...');
  fs.renameSync(oldVideoDir, newVideoDir);
} else if (!fs.existsSync(newVideoDir)) {
  console.error('❌ Error: demo_video directory not found in project root or public/! Please restore it.');
  process.exit(1);
}

// 2. Scan public/demo_video and generate public/videos.json
console.log('🔍 Scanning public/demo_video for video files...');
const files = fs.readdirSync(newVideoDir);
const videoFiles = files.filter(file => {
  const ext = path.extname(file).toLowerCase();
  return ext === '.mp4' || ext === '.webm' || ext === '.ogg';
});

const videos = videoFiles.map(filename => {
  const filePath = path.join(newVideoDir, filename);
  const stats = fs.statSync(filePath);
  return {
    filename,
    url: `demo_video/${encodeURIComponent(filename)}`,
    size: stats.size,
    mtime: stats.mtime
  };
});

// Sort by filename alphabetically (A-Z)
videos.sort((a, b) => a.filename.localeCompare(b.filename));

const outputJsonPath = path.join(publicDir, 'videos.json');
fs.writeFileSync(outputJsonPath, JSON.stringify({ success: true, videos }, null, 2));

console.log(`✅ Successfully generated: ${outputJsonPath}`);
console.log(`🎉 Found ${videos.length} videos. Your public/ folder is now a fully standalone static website!`);
