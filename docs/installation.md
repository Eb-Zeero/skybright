# Installation

## On your machine for development

Download the content of the repository as a zip file and extract the
file into a directory of your choice. Don't clone the repository.

Git must be installed in the development machine
You should then put the new directory (let's call it `/path/to/site`)
under version control.

```bash
cd /path/to/site
git init
```

Make sure you've installed [Java](http://www.oracle.com/technetwork/java/javase/downloads/index-jsp-138363.html)
and Python 3.5. Create a virtual environment
By running command:

```bash
python3 -m venv venv
```

virtual environment name must be venv else you will need to modify the
code framework and change venv to
name of you choice. (So just run the command as it is to simplify the
work).

Activate the virtual environment and install all the required Python
Libraries by running command:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

**note:** venv and everything on it must not be put in version control
since it will vary through machines and/or may cause confusion in the
server


## On a remote server

**Important note:** Do not install Apache. When the site is deployed, a
file .env is created, which contains settings which must be kept secret.
 Ensure that it is not put under version control.
Ubuntu 14.04 or higher must be running on the remote server, and
standard commands like `ssh` must be installed. The server should not be
used for anything other than running the deployed website.

**Note:** Python default version must not be change, and again Do not
install Apache if Apache is installed already uninstall it

Create a user `deploy` for deploying the site, and give that user sudo
permissions:

```bash
adduser deploy
gpasswd -a deploy sudo
```

**Important note:** Deploying user name, must be **deploy**( or code
framework must be modified)

Make sure wget is installed on the server.

Login as the deploy user.

Unless your repository has public access, you should also generate an
SSL key for the deploy user. Check whether there is a file
`~/.ssh/id_rsa.pub` already. If there isn't, create a new public key
by running

```bash
ssh-keygen
```

If you don't choose the default file location, you'll have to modify
the following instructions accordingly.

Once you have the key generated, find out whether the ssh agent is
running.

```bash
ps -e | grep [s]sh-agent
```

If agent isn't running, start it with

```bash
ssh-agent /bin/bash
```

Load your new key into the ssh agent:

```bash
ssh-add ~/.ssh/id_rsa
```

You can now view your public key by means of

```bash
cat ~/.ssh/id_rsa.pub
```

Refer to to the instructions for your repository host like Github or
Bitbucket as to how add your key top the host.

Once all the these prerequisites are in place you may deploy the site
by running

```bash
fab setup
```

Supervisor, which is used for running the Nginx server, logs both the
standard output and the standard error to log files in the folder
`/var/log/supervisor`. You should check these log files if the server
doesn't start.

If you get an internal server error after updating, there might still
be a uWSGI process bound to the requested port. Also, it seems that
sometimes changes aren't picked up after deployment, even though
Supervisor is restarted.

In these cases rebooting the server should help. You can easily force
the reboot by executing
 
 ```bash
 fab reboot
 ```

