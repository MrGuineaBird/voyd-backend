const express = require('express');
const multer = require('multer');

const app = express();
const PORT = process.env.PORT || 3000;

// Store videos in memory
const videos = [];

// Serve frontend
app.use(express.static('public'));

// Multer memory storage
const upload = multer({ storage: multer.memoryStorage() });

// Upload endpoint
app.post('/upload', upload.single('video'), (req, res) => {
    if (!req.file) return res.status(400).send('No file uploaded.');
    const id = Date.now().toString();
    videos.push({ id, buffer: req.file.buffer, mimetype: req.file.mimetype });
    res.json({ id });
});

// Serve video by id
app.get('/videos/:id', (req, res) => {
    const video = videos.find(v => v.id === req.params.id);
    if (!video) return res.status(404).send('Video not found');
    res.setHeader('Content-Type', video.mimetype);
    res.send(video.buffer);
});

// Feed endpoint
app.get('/feed', (req, res) => {
    const feed = videos.map(v => `/videos/${v.id}`);
    res.json(feed);
});

// Start server
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
