# Intelbras Solar Home Assistant Integration

Add to `configuration.yaml`
```
intelbras_solar:
  username: !secret intelbras_username
  password: !secret intelbras_password
```

Add to [`secrets.yaml`](https://www.home-assistant.io/docs/configuration/secrets/#using-secretsyaml)
```
intelbras_username: "John Smith"
intelbras_password: "my$secretPassW0rd"
```
