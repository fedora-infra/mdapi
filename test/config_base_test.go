package test

import (
	"metasource/metasource/config"
	"testing"
)

func TestMakeLogger(t *testing.T) {
	for _, iter := range []string{"info", "warn", "debug", "note"} {
		config.MakeLogger(&iter)
	}
}
