FROM python:3.12

# Install the application dependencies
COPY ./Server /home/src
RUN apt-get update && apt-get install -y libgl1
RUN pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu121
RUN bash /home/src/env_install.sh
RUN pip install --no-cache-dir -r /home/src/requirements.txt
RUN chmod -R a+rwx /usr/local/lib/python3.12/site-packages/pymatting


EXPOSE 8000


RUN useradd thesis2025
RUN chown -R thesis2025:thesis2025 /home/src
USER thesis2025
WORKDIR /home/src
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
