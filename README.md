# 🎨 XobehStudio - AI Image Generation Service

A powerful FastAPI-based service for generating high-quality images using Stable Diffusion 3.5 Large with GPU acceleration and advanced optimization features.

## 🌟 Features

- **🚀 GPU Acceleration**: Full CUDA support with 4-bit quantization for RTX 4060/4070
- **🎯 Latest AI Model**: Stable Diffusion 3.5 Large (2024) with superior image quality
- **💾 Memory Optimization**: 4-bit NF4 quantization + CPU offload for 8GB VRAM cards
- **📁 Local Model Storage**: Download once, run fast locally without re-downloading
- **🧠 Smart Loading**: Lazy initialization with local-first model loading
- **🎛️ Environment Configuration**: Comprehensive configuration via environment variables
- **📊 Real-time Monitoring**: Memory usage tracking and health checks
- **🔧 RESTful API**: Clean, well-documented API endpoints with interactive documentation
- **🐳 Docker Ready**: Containerized deployment with docker-compose support
- **📸 High Quality Output**: 1024x1024 images with enhanced prompt understanding

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- NVIDIA GPU with 8GB+ VRAM (RTX 4060 or better recommended)
- CUDA 12.1 or higher
- HuggingFace account and token
- pip package manager
- **Recommended**: NVIDIA GPU with 4GB+ VRAM and CUDA 11.7+ for optimal performance
- **Alternative**: Apple Silicon (MPS) or CPU support available

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd XobehStudio
   ```

2. **Set up environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env with your API keys and HuggingFace token
   # Get your token from: https://huggingface.co/settings/tokens
   # nano .env  # or use your preferred editor
   ```

3. **Install dependencies**
   
   **For CUDA (Recommended for NVIDIA GPUs):**
   ```bash
   # Install PyTorch with CUDA 12.1 support first
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   
   # Then install other requirements
   pip install -r requirements.txt
   ```
   
   **For CPU/MPS:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download the AI model (IMPORTANT - First Time Only)**
   ```bash
   # This downloads ~20-30GB model to local storage
   # Only needs to be done once!
   python download_model.py
   ```
   
   **Note**: The model download is mandatory for first-time setup. This ensures:
   - ⚡ Fast server startup (loads from local storage)
   - 🚫 No timeouts during API calls
   - 📶 Works offline after download
   - 💾 Efficient disk space usage with resume support

5. **Start the service**
   ```bash
   # Method 1: Direct run
   python app/main.py
   
   # Method 2: Uvicorn (recommended)
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the service**
   - Main interface: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

## ⚙️ Configuration

### Environment Variables

The service is fully configurable via environment variables. Key settings include:

#### API Keys (Required)
```env
GEMINI_API_KEY=your_gemini_api_key_here
HUGGINGFACE_TOKEN=your_huggingface_token_here
```

#### GPU/Device Configuration
```env
STABLE_DIFFUSION_DEVICE=cuda        # cuda, mps, or cpu
STABLE_DIFFUSION_TORCH_DTYPE=float16  # float16, float32, bfloat16
```

#### Model Selection
```env
STABLE_DIFFUSION_MODEL_ID=runwayml/stable-diffusion-v1-5
```

#### Performance Optimization
```env
ENABLE_MEMORY_EFFICIENT_ATTENTION=true
ENABLE_ATTENTION_SLICING=true
VAE_SLICING=true
ENABLE_CPU_OFFLOAD=false  # Set to true for low VRAM GPUs
```

See `.env.example` for complete configuration options and hardware-specific recommendations.

## 📋 API Endpoints

### Generate Image
**POST** `/api/v1/stable-diffusion/generate`

Generate an image from a text prompt with GPU acceleration.

**Request:**
```json
{
  "prompt": "A beautiful landscape with mountains and a lake at sunset, highly detailed, masterpiece"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Image generated successfully with Stable Diffusion",
  "image_url": "/images/sd_abc123def456.png"
}
```

### Health Check
**GET** `/api/v1/stable-diffusion/health`

Check service status and GPU information.

### Model Information
**GET** `/api/v1/stable-diffusion/info`

Get detailed model and configuration information.

### Memory Status
**GET** `/api/v1/stable-diffusion/memory`

Get current GPU/CPU memory usage.

### Cleanup Resources
**POST** `/api/v1/stable-diffusion/cleanup`

Free GPU memory and clean up resources.

## 🎯 Usage Examples

### Python Example with Error Handling
```python
import requests
from PIL import Image
import io

def generate_image(prompt: str, save_path: str = "generated.png"):
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/stable-diffusion/generate",
            json={"prompt": prompt},
            timeout=300  # 5 minutes timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Download the image
            image_response = requests.get(f"http://localhost:8000{result['image_url']}")
            
            # Save the image
            with open(save_path, 'wb') as f:
                f.write(image_response.content)
                
            print(f"Image saved to {save_path}")
            return save_path
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.Timeout:
        print("Request timed out. Image generation can take several minutes.")
    except Exception as e:
        print(f"Error: {e}")

# Generate an image
generate_image("A futuristic cyberpunk city at night, neon lights, highly detailed")
```

### Check System Status
```python
import requests

def check_system_status():
    # Health check
    health = requests.get("http://localhost:8000/api/v1/stable-diffusion/health")
    print("Health:", health.json())
    
    # Memory status (if GPU is available)
    memory = requests.get("http://localhost:8000/api/v1/stable-diffusion/memory")
    print("Memory:", memory.json())
    
    # Model info
    info = requests.get("http://localhost:8000/api/v1/stable-diffusion/info")
    print("Model Info:", info.json())

check_system_status()
```

## 🐳 Docker Deployment

### Quick Start with Docker Compose
```bash
# For GPU support (recommended)
docker-compose -f docker-compose.gpu.yml up -d

# For CPU-only deployment
docker-compose up -d
```

### Manual Docker Build
```bash
# Build the image
docker build -t xobehstudio .

# Run with GPU support
docker run --gpus all -p 8000:8000 -v $(pwd)/.env:/app/.env xobehstudio

# Run CPU-only
docker run -p 8000:8000 -v $(pwd)/.env:/app/.env xobehstudio
```

## 🔧 Hardware Requirements & Performance

### Recommended Specifications

#### High Performance Setup (Recommended)
- **GPU**: NVIDIA RTX 3060 (12GB) or better
- **RAM**: 16GB+
- **Storage**: 10GB+ free space for models
- **Expected Speed**: 2-5 seconds per image

#### Budget Setup
- **GPU**: NVIDIA GTX 1660 (6GB) or RTX 3050 (8GB)
- **RAM**: 12GB+
- **Storage**: 10GB+ free space
- **Expected Speed**: 5-15 seconds per image

#### CPU-Only Setup
- **CPU**: Modern multi-core processor (8+ cores recommended)
- **RAM**: 16GB+
- **Storage**: 10GB+ free space
- **Expected Speed**: 30-120 seconds per image

### Memory Optimization Tips

For **Low VRAM GPUs (4-6GB)**:
```env
ENABLE_MEMORY_EFFICIENT_ATTENTION=true
ENABLE_ATTENTION_SLICING=true
ENABLE_CPU_OFFLOAD=true
VAE_SLICING=true
IMAGE_WIDTH=512
IMAGE_HEIGHT=512
```

For **High VRAM GPUs (8GB+)**:
```env
ENABLE_MEMORY_EFFICIENT_ATTENTION=false
ENABLE_ATTENTION_SLICING=false
ENABLE_CPU_OFFLOAD=false
IMAGE_WIDTH=768
IMAGE_HEIGHT=768
```

## 🛠️ Troubleshooting

### Common Issues

1. **CUDA Out of Memory**
   ```bash
   # Solutions:
   # 1. Enable CPU offload in .env
   ENABLE_CPU_OFFLOAD=true
   
   # 2. Use smaller image dimensions
   IMAGE_WIDTH=512
   IMAGE_HEIGHT=512
   
   # 3. Call cleanup endpoint between generations
   curl -X POST http://localhost:8000/api/v1/stable-diffusion/cleanup
   ```

2. **Slow Generation Times**
   ```bash
   # Check if CUDA is being used
   curl http://localhost:8000/api/v1/stable-diffusion/health
   
   # Reduce steps for faster generation
   NUM_INFERENCE_STEPS=20
   ```

3. **Model Download Issues**
   - Ensure stable internet connection
   - Set HUGGINGFACE_TOKEN in .env file
   - Check available disk space (models are ~4GB each)

4. **Import Errors**
   ```bash
   # Reinstall PyTorch with correct CUDA version
   pip uninstall torch torchvision torchaudio
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

### Debug Mode
Enable debug logging for detailed troubleshooting:
```env
DEBUG=true
LOG_LEVEL=DEBUG
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8 isort

# Run tests
pytest

## Updated