# Bird or Squirrel

The smart bird feeder that tweets pictures of anything inside. This app uses a Raspberry Pi, camera, and IR break beam sensor. See the howchoo guide for an overview.

## To run

Install Docker, start the Docker container:

```
sudo docker run -d --restart=always \
        --device=/dev/mem:/dev/mem \
        --privileged \
        -e "TWITTER_ACCESS_TOKEN={your access token}" \
        -e "TWITTER_ACCESS_TOKEN_SECRET={your access token secret}" \
        -e "TWITTER_CONSUMER_KEY={your consumer key}" \
        -e "TWITTER_CONSUMER_SECRET={your consumer secret}" \
        howchoo/birdorsquirrel:latest
```

## See on Twitter

https://twitter.com/birdorsquirrel
