# Disk Full / No Space Left on Device

## Symptoms
Writes fail with `No space left on device` (errno 28). Services crash or refuse to start,
databases go read-only, and `df -h` shows a filesystem at 100% use.

## Likely causes
Most often runaway log files, an unrotated `/var/log`, large Docker images/volumes, or a
big temp/upload directory. Sometimes inodes are exhausted even though bytes are free -
check with `df -i`.

## Fix steps
1. Find the mount that is full: `df -h`. Then find big directories: `du -xhd1 /var | sort -h`.
2. Safest quick win: truncate a huge active log instead of deleting it:
   `truncate -s 0 /var/log/huge.log` (deleting a file an app still holds open does not free space).
3. Reclaim Docker space if this is a container host: `docker system df` then
   `docker system prune` (review what it will remove first).
4. Rotate logs going forward with logrotate so this does not recur.
5. If `df -i` shows inodes at 100%, delete large numbers of tiny files (often in a cache dir).

## Verify
`df -h` shows headroom on the affected mount and the failing service starts and stays up.
