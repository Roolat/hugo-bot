FROM python:alpine

# Source code location
WORKDIR /hugo

RUN \
# Update system and packages
       apk update \
    && apk upgrade \
# Install required dependencies
    && apk add --no-cache \
# # FFmpeg for concord-ext-audio (for video/audio decoding)
           ffmpeg \
# # We need gcc due to broken ctypes.util.find_library on alpine build...
           gcc \
# # Libsodium for PyNaCl
           libsodium \
# # Opus for discord.py voice support
           opus \
# Install build dependencies
    && apk add --no-cache --virtual .build-deps \
           curl \
           git \
           libffi-dev \
           make \
           musl-dev \
           python3-dev \
# Install Poetry and turn off virtual envs
    && curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python \
    && poetry config settings.virtualenvs.create false \
# Clone Hugo source code
    && git clone https://github.com/narimanized/hugo.git . \
# Install Python dependencies
    && poetry install -vvv \
    && poetry build -f sdist \
    && pip install dist/$(ls dist) \
# Clear Poetry cache
    && poetry cache:clear --all pypi \
# Clear build dependencies
    && apk del .build-deps

# Set executable
CMD ["python", "-m", "hugo"]
