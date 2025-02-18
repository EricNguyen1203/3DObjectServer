FROM continuumio/miniconda3

# Set working directory
WORKDIR /home/src

# Copy application source code
COPY ./Server /home/src

# Copy environment configuration files
COPY environment.yml /home/src/environment.yml

# Set default shell to use Conda
SHELL ["/bin/bash", "-c"]
RUN conda install -y python=3.12
# Create the Conda environment
RUN conda env create -f /home/src/environment.yml && conda clean --all -y

# Ensure Conda environment activation is persistent
RUN echo "source activate esroom" >> /etc/profile.d/conda.sh

# Install additional Python dependencies inside the Conda environment
RUN conda run -n esroom pip install --no-cache-dir -r /home/src/requirements.txt

# Expose the required port
EXPOSE 8000

# Create a non-root user with a home directory
RUN useradd -m thesis2025 && chown -R thesis2025:thesis2025 /home/src

# Switch to the non-root user
USER thesis2025

# Set working directory
WORKDIR /home/src

# Run the application with Conda environment activated
CMD ["bash", "-c", "source /etc/profile.d/conda.sh && conda activate esroom && uvicorn server:app --host 0.0.0.0 --port 8000"]