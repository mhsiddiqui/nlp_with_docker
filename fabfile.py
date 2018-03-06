from fabric.api import local


def deploy_tts():
    local('docker-compose stop')
    local('git pull origin master')
    local('docker-compose up --build -d')