FROM continuumio/miniconda3

# Set working directory
WORKDIR /home/src

# Copy application source code
COPY ./Server /home/src

# Step 1: Create Conda environment with Python version
RUN conda create -n hunyuan3d-1 python=3.9 && \
    conda clean --all -y

# Initialize Conda (for shell environment setup)
RUN echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc

COPY ./packages /opt/conda/envs/hunyuan3d-1/lib/python3.9/site-packages
## Install the correct pip version and Torch with CUDA support
#RUN /bin/bash -c "source /opt/conda/etc/profile.d/conda.sh && conda activate hunyuan3d-1 && pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121"

# Step 2: Install required Python packages from requirements.txt
RUN /bin/bash -c "source /opt/conda/etc/profile.d/conda.sh && conda activate hunyuan3d-1 && pip install --no-cache-dir -r /home/src/requirements.txt"

## Step 3: Run environment installation script
#RUN /bin/bash -c "source /opt/conda/etc/profile.d/conda.sh && conda activate hunyuan3d-1 && bash /home/src/env_install.sh"


# Expose the required port
EXPOSE 8000

# Create a non-root user with a home directory
RUN useradd -m thesis2025 && chown -R thesis2025:thesis2025 /home/src

# Switch to the non-root user
USER thesis2025

# Set working directory
WORKDIR /home/src

# Run the application
CMD ["bash", "-c", "source /etc/profile.d/conda.sh && conda activate hunyuan3d-1 && uvicorn server:app --host 0.0.0.0 --port 8000"]
