const express = require('express');
const app = express();
app.use(express.json());

const AVAILABLE_MODELS = [
  { id: "wan_2_1_cinema", name: "Wan 2.1 Cinema SOTA (14B)", media_type: "video", supports_camera_ctrl: true },
  { id: "ltx_video_realtime", name: "LTX-Video Real-Time Diffusion", media_type: "video", supports_camera_ctrl: true }
];

app.get('/api/v1/models', (req, res) => {
  res.json({ status: "success", models: AVAILABLE_MODELS });
});

app.post('/api/v1/generate', (req, res) => {
  const jobId = "job_" + Date.now();
  res.status(201).json({
    status: "queued",
    job_id: jobId,
    estimated_duration_sec: 24,
    message: "Dispatched to Zoho Catalyst Queue -> GPU Worker"
  });
});

app.get('/api/v1/jobs/poll/:id', (req, res) => {
  res.json({
    job_id: req.params.id,
    status: "COMPLETED",
    progress: 100,
    video_url: "https://project-rainfall-60091754575.development.catalystserverless.in/app/sample.mp4",
    duration_sec: 4.5,
    resolution: "1080p",
    cost_usd: 0.00
  });
});

module.exports = app;
