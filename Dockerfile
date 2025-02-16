FROM continuumio/miniconda3

# Install the application dependencies
COPY ./Server /home/src

# Set default shell to use Conda
SHELL ["/bin/bash", "-c"]

# Create and activate Conda environment
RUN conda create -n hunyuan3d-1 python=3.12 -y && \
    echo "conda activate hunyuan3d-1" >> ~/.bashrc

# Install PyTorch inside the Conda environment
RUN /bin/bash -c "source ~/.bashrc && conda activate hunyuan3d-1 && \
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121"

# Install other dependencies from requirements.txt
RUN /bin/bash -c "source ~/.bashrc && conda activate hunyuan3d-1 && \
    pip install --no-cache-dir -r /home/src/requirements.txt"

# Run environment setup script
RUN /bin/bash -c "source ~/.bashrc && conda activate hunyuan3d-1 && \
    bash env_install.sh"

# Expose the required port
EXPOSE 8000


RUN useradd thesis2025
RUN chown -R thesis2025:thesis2025 /home/src
USER thesis2025
WORKDIR /home/src
CMD ["/bin/bash", "-c", "source ~/.bashrc && conda activate hunyuan3d-1 && uvicorn server:app --host 0.0.0.0 --port 8000"]

