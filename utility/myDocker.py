#!/usr/bin/env python
# coding: utf-8

import docker
import threading


class ClientHandler(object):

    def __init__(self, **kwargs):
        self.dockerClient = docker.APIClient(**kwargs)

    def creatTerminalExec(self, containerId):
        execCommand = [
            "/bin/sh",
            "-c",
            'TERM=xterm-256color; export TERM; [ -x /bin/bash ] && ([ -x /usr/bin/script ] && /usr/bin/script -q -c "/bin/bash" /dev/null || exec /bin/bash) || exec /bin/sh']
        execOptions = {
            "tty": True,
            "stdin": True
        }
        execId = self.dockerClient.exec_create(containerId, execCommand, **execOptions)
        return execId["Id"]

    def startTerminalExec(self, execId):
        return self.dockerClient.exec_start(execId, socket=True, tty=True)


class DockerStreamThread(threading.Thread):
    def __init__(self, ws, terminalStream):
        super(DockerStreamThread, self).__init__()
        self.ws = ws
        self.terminalStream = terminalStream

    def run(self):
        while not self.ws.closed:
            try:
                dockerStreamStdout = self.terminalStream.recv(2048)
                if dockerStreamStdout is not None:
                    self.ws.send(str(dockerStreamStdout, encoding='utf-8'))
                else:
                    print("docker daemon socket is close")
                    self.ws.close()
            except Exception as e:
                print("docker daemon socket err: %s" % e)
                self.ws.close()
                break
