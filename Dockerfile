FROM ghcr.io/srekit/custom-images/base-python:pr-5-03c5622

COPY dist/*.whl ./

RUN pip install *.whl && rm -f *.whl

EXPOSE 8080

ENTRYPOINT ["python", "-m", "app"]
