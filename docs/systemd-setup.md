# Github SSH Setup


### Generate keys with 
```bash
ssh-keygen -t ed25519 -C "nishawl.naseer@outlook.com"
```

### Name it "github"
```bash
eval "$(ssh-agent -s)"
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
GRANT ALL PRIVILEGES ON *.* TO 'root'@'127.0.0.1' 
  IDENTIFIED BY '123' WITH GRANT OPTION;
```

### To reinit db, first enter python shell from root dir and execute this 
```python3
from src.utils.db_initialzation import main
main()
```
