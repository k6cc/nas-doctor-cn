//go:build windows

package main

// realDevID returns a fake device id on Windows.
// Since nas-doctor primarily runs on Docker/Linux, we mock this out
// for Windows builds to avoid syscall.Stat_t compilation errors.
func realDevID(path string) (uint64, error) {
	// Always return 0 so the persistence check gracefully skips/passes
	// without blowing up on Windows development machines.
	return 0, nil
}
