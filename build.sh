docker build -t rhodie/simple-python .
docker run -it --name flow_control -v $(pwd):/usr/src/app rhodie/simple-python