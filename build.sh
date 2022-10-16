docker build -t rhodie/flow_control_image .
docker run -it --name flow_control -v $(pwd):/usr/src/app rhodie/flow_control_image