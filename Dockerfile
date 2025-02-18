FROM continuumio/miniconda3

# Install the application dependencies
COPY ./Server /home/src

# Set default shell to use Conda
SHELL ["/bin/bash", "-c"]

COPY environment.yml /home/src/environment.yml
RUN conda env create -f /home/src/environment.yml
RUN pip install --no-cache-dir -r /home/src/requirements.txt
# Expose the required port
EXPOSE 8000


RUN useradd thesis2025
RUN chown -R thesis2025:thesis2025 /home/src
USER thesis2025
WORKDIR /home/src
CMD ["/bin/bash", "-c", "source ~/.bashrc && conda activate esroom && uvicorn server:app --host 0.0.0.0 --port 8000"]

