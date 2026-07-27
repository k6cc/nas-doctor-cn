// Process-group helpers stub for Windows.
// This allows the codebase to compile on Windows environments,
// even though the project primarily targets Linux/Darwin.

//go:build windows

package collector

import (
	"os/exec"
)

// setProcessGroup is a no-op on Windows.
// Windows does not use the Setpgid mechanism in the same way.
func setProcessGroup(cmd *exec.Cmd) {
	// No-op for Windows
}

// killProcessGroup falls back to standard Kill on Windows.
// Windows does not support negative-pid process group kills via syscall.Kill.
func killProcessGroup(cmd *exec.Cmd) {
	if cmd == nil || cmd.Process == nil {
		return
	}
	// Fall back to single-process kill on Windows
	_ = cmd.Process.Kill()
}
