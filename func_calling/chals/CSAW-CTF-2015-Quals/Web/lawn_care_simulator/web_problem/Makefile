all: tarball

tarball:
	mkdir -p deploy/
	cp -r db deploy/
	cp -r web deploy/
	cp docker-compose.yml deploy/
	cp ../bootstap.sh deploy/
	cp run.sh deploy/
	tar czvf deploy.tar.gz deploy/
	rm -rf deploy
