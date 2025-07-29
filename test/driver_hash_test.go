package test

import (
	"fmt"
	"metasource/metasource/config"
	"metasource/metasource/driver"
	"metasource/metasource/models/home"
	"path/filepath"
	"sync"
	"testing"
)

func TestVerifyChecksum_Failure_AbsentFile(t *testing.T) {
	var wait sync.WaitGroup
	name := "rawhide"

	Path_Init(t, "")

	cast := 0
	for _, iter := range []string{"filelists", "other", "primary"} {
		unit := home.FileUnit{
			Name: fmt.Sprintf("metasource-rawhide-%s.sqlite", iter),
			Path: filepath.Join(config.DBFOLDER, "zeroexistent", fmt.Sprintf("metasource-rawhide-%s.sqlite", iter)),
			Keep: false,
			Type: iter,
		}
		wait.Add(1)
		go driver.VerifyChecksum(&unit, &name, &wait, &cast)
	}
	wait.Wait()

	if cast != 0 {
		t.Errorf("Received %d, Expected 0", cast)
	}
}

func TestVerifyChecksum_Failure_MistakenHashType(t *testing.T) {
	var wait sync.WaitGroup
	name := "rawhide"

	Path_Init(t, "")

	cast := 0
	for _, iter := range []string{"filelists", "other", "primary"} {
		unit := home.FileUnit{
			Name: fmt.Sprintf("metasource-rawhide-%s.sqlite", iter),
			Path: filepath.Join(config.DBFOLDER, fmt.Sprintf("metasource-rawhide-%s.sqlite", iter)),
			Keep: false,
			Type: iter,
			Hash: home.Checksum{
				Type: "mistaken-hash-type",
				Data: "",
			},
		}
		wait.Add(1)
		go driver.VerifyChecksum(&unit, &name, &wait, &cast)
	}
	wait.Wait()

	if cast != 0 {
		t.Errorf("Received %d, Expected 0", cast)
	}
}

func TestVerifyChecksum_Failure_MistakenHashData(t *testing.T) {
	var wait sync.WaitGroup
	name := "rawhide"

	Path_Init(t, "")

	cast := 0
	for _, iter := range []string{"filelists", "other", "primary"} {
		unit := home.FileUnit{
			Name: fmt.Sprintf("metasource-rawhide-%s.sqlite", iter),
			Path: filepath.Join(config.DBFOLDER, fmt.Sprintf("metasource-rawhide-%s.sqlite", iter)),
			Keep: false,
			Type: iter,
			Hash: home.Checksum{
				Type: "sha256",
				Data: "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
			},
		}
		wait.Add(1)
		go driver.VerifyChecksum(&unit, &name, &wait, &cast)
	}
	wait.Wait()

	if cast != 0 {
		t.Errorf("Received %d, Expected 0", cast)
	}
}
