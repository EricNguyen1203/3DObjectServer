FROM continuumio/miniconda3

# Set working directory
WORKDIR /home/src

# Copy application source code
COPY ./Server /home/src

# Copy environment configuration files
COPY environment.yml /home/src/environment.yml

# Set default shell to use Conda
SHELL ["/bin/bash", "-c"]

# Create the Conda environment
RUN conda env create -f /home/src/environment.yml && conda clean --all -y

# Ensure the Conda environment is available when using bash
RUN echo "source activate esroom" >> ~/.bashrc

# Install additional Python dependencies inside the Conda environment
RUN conda run -n esroom pip install --no-cache-dir -r /home/src/requirements.txt

# Expose the required port
EXPOSE 8000

# Create a non-root user and change ownership
RUN useradd -m thesis2025 && chown -R thesis2025:thesis2025 /home/src

# Switch to the non-root user
USER thesis2025

# Set working directory as the copied source folder
WORKDIR /home/src

# Run the
