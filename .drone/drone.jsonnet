local publishDocker() = {
  name: "publish-docker",
  kind: "pipeline",
  type: "docker",
  volumes: [{name: "docker", host: {path: "/var/run/docker.sock"}}],
  steps: [{
    name: "build-and-publish",
    image: "docker",
    volumes: [{name: "docker", path: "/var/run/docker.sock"}],
    environment: {
      proget_api_key: {from_secret: "proget_api_key"}
    },
    commands: [
      "apk add --no-cache bash",
      ".drone/scripts/build-and-publish.sh"
    ]
  }]
};

[
  publishDocker()
]
