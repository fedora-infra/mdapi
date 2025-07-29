package test

import (
	"metasource/metasource/config"
	"testing"
)

func TestSetLogger(t *testing.T) {
	for _, iter := range []string{"info", "warn", "debug", "note"} {
		config.SetLogger(&iter)
	}
}
