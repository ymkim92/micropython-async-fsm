# Async FSM for micropython

![ESP32](https://img.shields.io/badge/ESP-32-000000.svg?longCache=true&style=flat&colorA=CC101F)
![CI](https://github.com/ymkim92/micropython-async-fsm/actions/workflows/ci.yml/badge.svg)

 
### Using mip via mpremote:

```
$ mpremote mip install github:ymkim92/micropython-async-fsm
```

### Using mip directly on a WiFi capable board:

```
>>> import mip
>>> mip.install("github:ymkim92/micropython-async_fsm")
```

### justfile

You can use this during development.

Upload the scripts to a target device:

```sh
$ just upload
```

You can run unittest:

```sh
$ just run-test
```