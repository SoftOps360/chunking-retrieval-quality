# Out Of Memory (OOM) - Process Killed

## Symptoms
A process disappears with no application-level error. `dmesg` or the kernel log shows
`Out of memory: Killed process 2417 (python)`. On Kubernetes the pod shows
`OOMKilled` with exit code 137 and restarts in a loop.

## Likely causes
The host or container ran out of memory and the Linux OOM killer terminated the biggest
offender. Causes: a real memory leak in the app, a memory limit set too low for normal
load, a batch job loading too much into memory at once, or too many worker processes.

## Fix steps
1. Confirm it was the OOM killer: `dmesg -T | grep -i oom` or check the kernel log.
2. On Kubernetes, `kubectl describe pod <pod>` - look for `Reason: OOMKilled`, exit code 137.
3. Short term, raise the memory limit (container `--memory` / pod `resources.limits.memory`)
   if the limit is simply too tight for real usage.
4. Long term, profile the app for a leak, cap worker count, or stream large jobs instead
   of loading everything into memory.

## Verify
The process/pod stays up under normal load and memory usage plateaus instead of climbing
until it is killed again.
