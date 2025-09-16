# VPS Deployment Configuration

## Setting up for VPS Deployment

To deploy on a VPS and make images/videos accessible via your VPS IP address, follow these steps:

### 1. Create .env file

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

### 2. Configure BASE_URL for your VPS

Edit the `.env` file and update the BASE_URL:

**For VPS deployment:**
```bash
BASE_URL=http://YOUR_VPS_IP:5642
```

**For domain with SSL:**
```bash
BASE_URL=https://yourdomain.com
```

**Example with actual IP:**
```bash
BASE_URL=http://203.0.113.123:5642
```

### 3. Add your API keys

Update the following in your `.env` file:
```bash
GEMINI_API_KEY=your_actual_gemini_api_key
OPEN_AI_API_KEY=your_actual_openai_api_key
FAL_API_KEY=your_actual_fal_api_key
```

### 4. Deploy

```bash
docker-compose up --build -d
```

### 5. Test

After deployment, your generated images will be accessible at:
- `http://YOUR_VPS_IP:5642/images/filename.png`
- `http://YOUR_VPS_IP:5642/videos/filename.mp4`
- `http://YOUR_VPS_IP:5642/audio/filename.mp3`

### Port Configuration

- **5642**: Main application port (nginx proxy)
- **442**: Secondary port (can be used for SSL in future)
- **8069**: Internal FastAPI port (not exposed externally)

### Directory Structure

The application creates and serves files from:
- `./generated_images` → served at `/images/`
- `./generated_videos` → served at `/videos/`
- `./generated_audio` → served at `/audio/`

These directories are automatically mounted and persistent across container restarts.