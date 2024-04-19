# Github SSH Setup


### Generate keys with 
```bash
ssh-keygen -t ed25519 -C "nishawl.naseer@outlook.com"
```

### Name it "github"
```bash
ssh-add ~/uweflix-backend/github
```

### Clone git project
```bash
git clone git@github.com:nishaalnaseer/uweflix-backend.git
```

### Bash scripts are in ```docs/bash-files```
### Installation 
### Create service 
### Enable the service
### If all goes well you should be seen the status from systemd

### View log from start with 
```bash
journalctl --user -u uweflix-backend
```

### View log from tail with 
```bash
journalctl --user -u uweflix-backend -r
```

### Follow log with
```bash
journalctl --user -u uweflix-backend -f
```

### Grant rights to user root with 
```
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' 
  IDENTIFIED BY '123' WITH GRANT OPTION;
```
