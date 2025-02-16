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
# Run environment setup script
RUN /bin/bash -c "source ~/.bashrc && conda activate hunyuan3d-1 && \
    bash /home/src/env_install.sh"
RUN curl -LO https://github.com/NVIDIA/cub/archive/1.10.0.tar.gz && tar xzf 1.10.0.tar.gz && export CUB_HOME=$PWD/cub-1.10.0 && rm -f 1.10.0.tar.gz
RUN /bin/bash -c "source ~/.bashrc && conda activate hunyuan3d-1 && \
    CUB_HOME=$PWD/cub-1.10.0 pip install 'git+https://github.com/facebookresearch/pytorch3d.git'"
# Expose the required port
EXPOSE 8000


RUN useradd thesis2025
RUN chown -R thesis2025:thesis2025 /home/src
USER thesis2025
WORKDIR /home/src
CMD ["/bin/bash", "-c", "source ~/.bashrc && conda activate hunyuan3d-1 && uvicorn server:app --host 0.0.0.0 --port 8000"]

