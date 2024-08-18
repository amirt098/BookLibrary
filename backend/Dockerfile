ARG TAG=latest
FROM nexus.runc.info/moneyro/baseimage:$TAG AS build_env

RUN apt install --no-install-recommends -y \
    python3-dev \
    build-essential


RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --index-url https://nexus.runc.info/repository/pypi-group/simple --no-cache-dir -r requirements.txt


FROM nexus.runc.info/moneyro/baseimage:$TAG


WORKDIR /code
COPY --from=build_env /venv /venv
ENV PATH="/venv/bin:$PATH"

COPY . .
EXPOSE 8000
CMD ["/bin/bash", "./run.sh"]
