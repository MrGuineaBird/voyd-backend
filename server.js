// server.js
const express = require('express');
const multer = require('multer');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Memory storage for uploaded files
const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

// Serve static frontend
app.use(express.static('frontend'));

// Handle video upload
app.post('/upload', upload.single('video'), (req, res) => {
    if (!req.file) {
        return res.status(400).send('No file uploaded.');
    }

    // Convert uploaded file buffer to a Base64 URL so frontend can play it
    const videoBase64 = req.file.buffer.toString('base64');
    const mimeType = req.file.mimetype;
    const videoURL = `data:${mimeType};base64,${videoBase64}`;

    res.send(`
        <h2>Uploaded Video</h2>
        <video width="640" controls>
            <source src="${videoURL}" type="${mimeType}">
            Your browser does not support the video tag.
        </video>
        <br><a href="/">Upload another video</a>
    `);
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
