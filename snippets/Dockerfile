FROM skhatiri/aerialist:latest
RUN pip3 install -e /src/aerialist/

COPY ./requirements.txt /src/generator/requirements.txt
WORKDIR /src/generator/
RUN pip3 install -r /src/generator/requirements.txt

COPY ./ /src/generator/
RUN mkdir -p ./logs/ ./results/ ./generated_tests/

ENV AGENT local
ENV AVOIDANCE_LAUNCH /src/aerialist/aerialist/resources/simulation/collision_prevention.launch
ENV AVOIDANCE_BOX /src/aerialist/aerialist/resources/simulation/box.xacro
