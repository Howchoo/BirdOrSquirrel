# Bird or Squirrel

The smart bird feeder that tweets pictures of anything inside. This app uses a Raspberry Pi, camera, and IR break beam sensor. See the howchoo guide for an overview.

## To run

Install Docker.

Start the Docker container:

```
docker run --restart=always --device=/dev/mem:/dev/mem --privileged howchoo/birdorsquirrel:latest
```
