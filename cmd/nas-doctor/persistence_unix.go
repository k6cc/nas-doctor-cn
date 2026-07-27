//go:build !windows

package main

import (
	"syscall"
)

// realDevID returns the device id that the given path currently lives on.
// On Linux this is populated by the kernel from the inode's superblock,
// so a bind-mounted /data (hosted by a real filesystem on the host) will
// have a different Dev than / (the container's overlay rootfs).
func realDevID(path string) (uint64, error) {
	var st syscall.Stat_t
	if err := syscall.Stat(path, &st); err != nil {
		return 0, err
	}
	return uint64(st.Dev), nil
}
