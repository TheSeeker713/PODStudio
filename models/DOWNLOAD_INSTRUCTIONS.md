# Model Download Instructions

This document provides instructions for downloading the necessary models for the image generation module.

## 1. Stable Diffusion XL (SDXL)

The recommended base model for SDXL is the official model from Stability AI. You will need the base model, the refiner, and the VAE.

- **SDXL Base 1.0:** [Download from Hugging Face](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/tree/main)
- **SDXL Refiner 1.0:** [Download from Hugging Face](https://huggingface.co/stabilityai/stable-diffusion-xl-refiner-1.0/tree/main)
- **SDXL VAE:** [Download from Hugging Face](https://huggingface.co/madebyollin/sdxl-vae-fp16-fix/tree/main)

Download the `.safetensors` files from each of these repositories and place them in the `models/sdxl` directory.

## 2. Stable Diffusion 3 (SD3)

Stable Diffusion 3 is available in a few different sizes. The medium model is a good starting point.

- **SD3 Medium:** [Download from Hugging Face](https://huggingface.co/stabilityai/stable-diffusion-3-medium-diffusers)

Download the entire model repository and place it in `models/sd3/medium`.

## 3. FLUX

FLUX is a newer architecture. We will use the "schnell" version which is designed for high-speed inference.

- **FLUX.1-schnell:** [Download from Hugging Face](https://huggingface.co/black-forest-labs/FLUX.1-schnell)

Download the entire model repository and place it in `models/flux/schnell`.

## Directory Structure

After downloading, your `models` directory should look like this:

```
models/
├── sdxl/
│   ├── sdxl_base_1.0.safetensors
│   ├── sdxl_refiner_1.0.safetensors
│   └── sdxl_vae.safetensors
├── sd3/
│   └── medium/
│       ├── ... (model files)
└── flux/
    └── schnell/
        ├── ... (model files)
```
