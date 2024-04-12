
docker build . -t aggregator

docker run -p 8020:8020 -it -v ./code --rm aggregator 
