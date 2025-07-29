package test

import (
	"fmt"
	"metasource/metasource/config"
	"metasource/metasource/driver"
	"metasource/metasource/models/home"
	"path/filepath"
	"testing"
)

func TestGenerateSignal_Failure_FaultyFile(t *testing.T) {
	Path_Init_Faulty(t)

	cast := 0
	for _, iter := range []string{"filelists", "other", "primary"} {
		unit := home.FileUnit{
			Name: fmt.Sprintf("metasource-rawhide-%s.sqlite", iter),
			Path: filepath.Join(config.DBFOLDER, fmt.Sprintf("metasource-rawhide-%s.sqlite", iter)),
			Keep: false,
			Type: iter,
		}
		expt := driver.GenerateSignal(&unit, &cast)
		if expt == nil {
			t.Errorf("Received nothing, Expected error")
		} else if expt.Error() != "file is not a database" {
			t.Errorf("Received '%s', Expected 'file is not a database'", expt.Error())
		}
	}
}

func TestGenerateSignal_Failure_FaultyDriver(t *testing.T) {
	Path_Init(t, "")

	original := config.DBDRIVER
	config.DBDRIVER = "very-good-database-driver"
	defer func() { config.DBDRIVER = original }()

	cast := 0
	for _, iter := range []string{"filelists", "other", "primary"} {
		unit := home.FileUnit{
			Name: fmt.Sprintf("metasource-rawhide-%s.sqlite", iter),
			Path: filepath.Join(config.DBFOLDER, fmt.Sprintf("metasource-rawhide-%s.sqlite", iter)),
			Keep: false,
			Type: iter,
		}
		expt := driver.GenerateSignal(&unit, &cast)
		if expt == nil {
			t.Errorf("Received nothing, Expected error")
		} else if expt.Error() != "sql: unknown driver \"very-good-database-driver\" (forgotten import?)" {
			t.Errorf("Received '%s', Expected 'sql: unknown driver \"very-good-database-driver\" (forgotten import?)'", expt.Error())
		}
	}
}
