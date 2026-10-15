# Current Cluster Pointers

This directory is intentionally empty until the first cluster candidate is
created. Argo's environment overlays point at an exact file in this directory;
when the file does not exist, the ApplicationSet creates no runtime
Applications. This prevents an uninitialized cluster from consuming null
candidate, chart, or revision values.

The cluster deployment workflow creates the environment pointer only after it
has written and committed a valid cluster candidate.
