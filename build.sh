cd back-end

echo STOPPING DOCKER
docker stop $(docker ps -a -q)
docker rm -vf $(docker ps -aq)
docker rm $(docker ps -a -q)

cd ../front-end

echo BUILDING FRONT
docker build -t my-vue-app .
id=$(docker run -d my-vue-app)

docker wait $id

cd ../back-end

#rm -rf dist
#docker cp $id:/app/dist .

echo STOPPING DOCKER
docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)

ls

echo RUNNING DOCKER
docker compose build > ../buildlog.txt
docker compose up --detach