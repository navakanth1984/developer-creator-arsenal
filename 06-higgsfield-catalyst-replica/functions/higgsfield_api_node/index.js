const express = require('express');
const app = express();
app.use(express.json());

const AVAILABLE_MODELS = [
  { id: "wan_2_1_cinema", name: "Wan 2.1 Cinema SOTA (14B)", media_type: "video", supports_camera_ctrl: true },
  { id: "ltx_video_realtime", name: "LTX-Video Real-Time Diffusion", media_type: "video", supports_camera_ctrl: true }
];

let jobs = {};

app.get('/api/v1/models', (req, res) => {
  res.json({ status: "success", models: AVAILABLE_MODELS });
});

app.post('/api/v1/generate', (req, res) => {
  const jobId = "job_" + Date.now();
  const job = {
    job_id: jobId,
    prompt: (req.body && req.body.prompt) || "Cinematic drone sweep over cybernetic landscape, 8k",
    model: (req.body && req.body.model) || "wan_2_1_cinema",
    camera_vector: (req.body && req.body.camera_vector) || { pan: 0.0, tilt: -0.15, zoom: 1.4, roll: 0.0 },
    status: "queued",
    created_at: new Date().toISOString()
  };
  jobs[jobId] = job;
  res.status(201).json({
    status: "queued",
    job_id: jobId,
    estimated_duration_sec: 24,
    message: "Dispatched to Zoho Catalyst Queue -> GPU Worker"
  });
});

app.get('/api/v1/jobs/pending', (req, res) => {
  const pending = Object.values(jobs).filter(j => j.status === 'queued');
  res.json({ status: "success", count: pending.length, jobs: pending });
});

app.post('/api/v1/jobs/:id/complete', (req, res) => {
  const job = jobs[req.params.id];
  if (job) {
    job.status = "COMPLETED";
    job.progress = 100;
    job.video_url = (req.body && req.body.video_url) || "https://project-rainfall-60091754575.development.catalystserverless.in/app/sample.mp4";
    job.duration_sec = (req.body && req.body.duration_sec) || 4.5;
    return res.json({ status: "success", job });
  }
  res.status(404).json({ error: "Job not found" });
});

app.get('/api/v1/jobs/poll/:id', (req, res) => {
  const job = jobs[req.params.id];
  if (job) {
    return res.json(job);
  }
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
