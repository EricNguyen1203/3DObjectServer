FROM python:3.12

# Install the application dependencies
COPY ./Server /home/src
RUN pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu121
RUN pip3 install -r /home/src/gen3d/requirements.txt --index-url https://download.pytorch.org/whl/cu121
RUN pip3 install git+https://github.com/facebookresearch/pytorch3d@stable
RUN pip3 install git+https://github.com/NVlabs/nvdiffrast
RUN pip install --no-cache-dir -r /home/src/requirements.txt

EXPOSE 8000


RUN useradd thesis2025
RUN chown -R thesis2025:thesis2025 /home/src
USER thesis2025
WORKDIR /home/src
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
