# Lawn Care Simulator

## Author
Beastes
## Points
200
## Category
Web
## Description

## Flag
`667e217666098fd0d8055c04c71bebc7`
## Solution
`solve.py`
Starting off, the first thing to notice is that the login form hashes the password client-side, then submits the hash to the server.
After browsing around the website, you might notice that one of the pages makes a request to .git/refs/heads/master, meaning that the git repo for this code is publicly accessible.
From there, clone the repo and get some of the source code: `git clone http://<url>/.git`
Now, looking at the code, you can pretty easily determine that the password validation code is vulnerable to a timing attack. By guessing one letter at a time and measuring the request time, you can get the correct password hash.
The last thing you need is a correct username. The source code sign_up.php uses a LIKE comparison in a sql statement. If you try to sign up as the user %, it will tell you that the ~~FLAG~~ user is already taken.
With the correct username, you can write a script to guess the ~~FLAG~~ user's password hash. Once you do this, the page will give you the flag.
To address latency issues, we can increase the usleep delay in the password validation code, and also reduce the number of characters of the password hash that are checked before it returns true. There are also ways to overcome the latency issues when you write the guessing script, so a bit of variablility in latency could be an interesting part of the problem.
## Setup
```
cd web_problem/
make tarball
<scp the tarball somwhere>
<untar the tarball>
./bootstrap.sh
./run.sh
```
## Notes
* Generally just running ./run.sh should reset the problem, taking in any changes you made to files outside of the containers.
* If the guess part is an issue for people, replace one of the eariler characters in the hash in create_tables.sql with a 0. Make sure the lenght of this hash is still 32 characters.
* To tail the web server logs, on the host run `docker logs -f timing_web`
* To give yourself a shell in one of the containers (timing_web or timing_db): `docker exec -it timing_web bash -l`
* To stop/remove a container: `docker stop timing_web && docker rm timing_web`
* If you randomly run out of disk space on the host, you might have to many docker images sitting around. List them with `docker images`, and remove them with `docker rmi <image>`
