package test

import (
	"fmt"
	"metasource/metasource/config"
	"metasource/metasource/driver"
	"metasource/metasource/models"
	"os"
	"testing"
)

func TestKillObsoleteBranches_ObsoleteDeleted(t *testing.T) {
	basepath := "./assets"
	destpath := fmt.Sprintf("%s/test-%s", basepath, driver.GenerateIdentity(&config.RANDOM_LENGTH))
	_ = os.MkdirAll(destpath, 0750)

	origpath := config.DBFOLDER
	config.DBFOLDER = destpath
	t.Cleanup(func() {
		config.DBFOLDER = origpath
		WipeGeneration(destpath)
	})

	for _, name := range []string{
		"metasource-f41-primary.sqlite",
		"metasource-f41-filelists.sqlite",
		"metasource-f41-other.sqlite",
		"metasource-f41-updates-primary.sqlite",
		"metasource-f41-updates-filelists.sqlite",
		"metasource-f41-updates-other.sqlite",
	} {
		_ = os.WriteFile(fmt.Sprintf("%s/%s", destpath, name), []byte("test"), 0600)
	}

	active := []models.LinkUnit{
		{Name: "f44"},
		{Name: "f44-updates"},
		{Name: "rawhide"},
	}

	expt := driver.KillObsoleteBranches(active)
	if expt != nil {
		t.Errorf("Received '%s', Expected nothing", expt.Error())
	}

	files, _ := os.ReadDir(destpath)
	if len(files) != 0 {
		t.Errorf("Received %d files remaining, Expected 0", len(files))
	}
}

func TestKillObsoleteBranches_PreserveActiveBranches(t *testing.T) {
	basepath := "./assets"
	destpath := fmt.Sprintf("%s/test-%s", basepath, driver.GenerateIdentity(&config.RANDOM_LENGTH))
	_ = os.MkdirAll(destpath, 0750)

	origpath := config.DBFOLDER
	config.DBFOLDER = destpath
	t.Cleanup(func() {
		config.DBFOLDER = origpath
		WipeGeneration(destpath)
	})

	activeFiles := []string{
		"metasource-f44-primary.sqlite",
		"metasource-f44-filelists.sqlite",
		"metasource-f44-other.sqlite",
		"metasource-f44-updates-primary.sqlite",
		"metasource-f44-updates-testing-primary.sqlite",
		"metasource-rawhide-primary.sqlite",
	}
	for _, name := range activeFiles {
		_ = os.WriteFile(fmt.Sprintf("%s/%s", destpath, name), []byte("test"), 0600)
	}

	active := []models.LinkUnit{
		{Name: "f44"},
		{Name: "f44-updates"},
		{Name: "f44-updates-testing"},
		{Name: "src_f44"},
		{Name: "rawhide"},
	}

	expt := driver.KillObsoleteBranches(active)
	if expt != nil {
		t.Errorf("Received '%s', Expected nothing", expt.Error())
	}

	files, _ := os.ReadDir(destpath)
	if len(files) != len(activeFiles) {
		t.Errorf("Received %d files remaining, Expected %d", len(files), len(activeFiles))
	}
}

func TestKillObsoleteBranches_MixingBranches(t *testing.T) {
	basepath := "./assets"
	destpath := fmt.Sprintf("%s/test-%s", basepath, driver.GenerateIdentity(&config.RANDOM_LENGTH))
	_ = os.MkdirAll(destpath, 0750)

	origpath := config.DBFOLDER
	config.DBFOLDER = destpath
	t.Cleanup(func() {
		config.DBFOLDER = origpath
		WipeGeneration(destpath)
	})

	for _, name := range []string{
		"metasource-f44-primary.sqlite",
		"metasource-f44-updates-primary.sqlite",
		"metasource-f40-primary.sqlite",
		"metasource-f40-updates-primary.sqlite",
		"metasource-rawhide-primary.sqlite",
		"metasource-rawhide-updates-primary.sqlite",
	} {
		_ = os.WriteFile(fmt.Sprintf("%s/%s", destpath, name), []byte("test"), 0600)
	}

	active := []models.LinkUnit{
		{Name: "f44"},
		{Name: "f44-updates"},
		{Name: "rawhide"},
	}

	expt := driver.KillObsoleteBranches(active)
	if expt != nil {
		t.Errorf("Received '%s', Expected nothing", expt.Error())
	}

	files, _ := os.ReadDir(destpath)
	if len(files) != 4 {
		t.Errorf("Received %d files remaining, Expected 4", len(files))
	}

	expected := map[string]bool{
		"metasource-f44-primary.sqlite":             true,
		"metasource-f44-updates-primary.sqlite":     true,
		"metasource-rawhide-primary.sqlite":         true,
		"metasource-rawhide-updates-primary.sqlite": true,
	}
	for _, file := range files {
		if !expected[file.Name()] {
			t.Errorf("Unexpected file remaining: %s", file.Name())
		}
	}
}

func TestKillObsoleteBranches_FolderUnoccupied(t *testing.T) {
	basepath := "./assets"
	destpath := fmt.Sprintf("%s/test-%s", basepath, driver.GenerateIdentity(&config.RANDOM_LENGTH))
	_ = os.MkdirAll(destpath, 0750)

	origpath := config.DBFOLDER
	config.DBFOLDER = destpath
	t.Cleanup(func() {
		config.DBFOLDER = origpath
		WipeGeneration(destpath)
	})

	active := []models.LinkUnit{{Name: "f44"}}

	expt := driver.KillObsoleteBranches(active)
	if expt != nil {
		t.Errorf("Received '%s', Expected nothing", expt.Error())
	}
}

func TestKillObsoleteBranches_FolderGone(t *testing.T) {
	origpath := config.DBFOLDER
	config.DBFOLDER = fmt.Sprintf("/var/tmp/test-%s", driver.GenerateIdentity(&config.RANDOM_LENGTH))
	defer func() { config.DBFOLDER = origpath }()

	active := []models.LinkUnit{{Name: "f44"}}

	expt := driver.KillObsoleteBranches(active)
	if expt == nil {
		t.Errorf("Received nothing, Expected error")
	}
}

func TestKillObsoleteBranches_SkipFolder(t *testing.T) {
	basepath := "./assets"
	destpath := fmt.Sprintf("%s/test-%s", basepath, driver.GenerateIdentity(&config.RANDOM_LENGTH))
	_ = os.MkdirAll(destpath, 0750)

	origpath := config.DBFOLDER
	config.DBFOLDER = destpath
	t.Cleanup(func() {
		config.DBFOLDER = origpath
		WipeGeneration(destpath)
	})

	_ = os.MkdirAll(fmt.Sprintf("%s/metasource-f41-primary.sqlite", destpath), 0750)
	_ = os.WriteFile(fmt.Sprintf("%s/metasource-f44-primary.sqlite", destpath), []byte("test"), 0600)

	active := []models.LinkUnit{{Name: "f44"}}

	expt := driver.KillObsoleteBranches(active)
	if expt != nil {
		t.Errorf("Received '%s', Expected nothing", expt.Error())
	}

	files, _ := os.ReadDir(destpath)
	if len(files) != 2 {
		t.Errorf("Received %d entries remaining, Expected 2 (1 dir + 1 file)", len(files))
	}
}

func TestKillObsoleteBranches_SkipMiscFile(t *testing.T) {
	basepath := "./assets"
	destpath := fmt.Sprintf("%s/test-%s", basepath, driver.GenerateIdentity(&config.RANDOM_LENGTH))
	_ = os.MkdirAll(destpath, 0750)

	origpath := config.DBFOLDER
	config.DBFOLDER = destpath
	t.Cleanup(func() {
		config.DBFOLDER = origpath
		WipeGeneration(destpath)
	})

	_ = os.WriteFile(fmt.Sprintf("%s/metasource-f41-primary.xml", destpath), []byte("test"), 0600)
	_ = os.WriteFile(fmt.Sprintf("%s/some-misc-file.txt", destpath), []byte("test"), 0600)

	active := []models.LinkUnit{{Name: "f44"}}

	expt := driver.KillObsoleteBranches(active)
	if expt != nil {
		t.Errorf("Received '%s', Expected nothing", expt.Error())
	}

	files, _ := os.ReadDir(destpath)
	if len(files) != 2 {
		t.Errorf("Received %d files remaining, Expected 2", len(files))
	}
}
