package test

import (
	"fmt"
	"metasource/metasource/config"
	"metasource/metasource/driver"
	"metasource/metasource/lookup"
	"testing"
)

func TestReadPrmy_Failure_AbsentDB(t *testing.T) {
	original := config.DBFOLDER
	config.DBFOLDER = fmt.Sprintf("/var/tmp/test-%s", driver.GenerateIdentity(&config.RANDOM_LENGTH))
	defer func() { config.DBFOLDER = original }()

	vers, name := "rawhide", "systemd"
	_, _, expt := lookup.ReadPrmy(&vers, &name)
	if expt == nil {
		t.Errorf("Received nothing, Expected error")
	} else if expt.Error() != "database file does not exist" {
		t.Errorf("Received '%s', Expected 'database file does not exist'", expt.Error())
	}
}

func TestReadPrmy_Failure_FaultyDB(t *testing.T) {
	Path_Init_Faulty(t)

	vers, name := "rawhide", "systemd"
	_, _, expt := lookup.ReadPrmy(&vers, &name)
	if expt == nil {
		t.Errorf("Received nothing, Expected error")
	} else if expt.Error() != "file is not a database" {
		t.Errorf("Received '%s', Expected 'file is not a database'", expt.Error())
	}
}

func TestReadPrmy_Failure_FaultyDriver(t *testing.T) {
	Path_Init(t, "")

	original := config.DBDRIVER
	config.DBDRIVER = "very-good-database-driver"
	defer func() { config.DBDRIVER = original }()

	vers, name := "rawhide", "systemd"
	_, _, expt := lookup.ReadPrmy(&vers, &name)
	if expt == nil {
		t.Errorf("Received nothing, Expected error")
	} else if expt.Error() != "sql: unknown driver \"very-good-database-driver\" (forgotten import?)" {
		t.Errorf("Received '%s', Expected 'sql: unknown driver \"very-good-database-driver\" (forgotten import?)'", expt.Error())
	}
}

func TestReadPrmy_Failure_FaultyPlea(t *testing.T) {
	Path_Init(t, "")

	original := config.OBTAIN_PACKAGE
	config.OBTAIN_PACKAGE = "SELECT name, arch FROM packages WHERE name = ? ORDER BY epoch DESC, version DESC, release DESC"
	defer func() { config.OBTAIN_PACKAGE = original }()

	vers, name := "rawhide", "systemd"
	_, _, expt := lookup.ReadPrmy(&vers, &name)
	if expt == nil {
		t.Errorf("Received nothing, Expected error")
	} else if expt.Error() != "sql: expected 2 destination arguments in Scan, not 11" {
		t.Errorf("Received '%s', Expected 'sql: expected 2 destination arguments in Scan, not 11'", expt.Error())
	}
}

func TestReadPrmy_Failure_FaultyName(t *testing.T) {
	Path_Init(t, "")

	vers, name := "rawhide", ""
	_, _, expt := lookup.ReadPrmy(&vers, &name)
	if expt == nil {
		t.Errorf("Received nothing, Expected error")
	} else if expt.Error() != "no result found" {
		t.Errorf("Received '%s', Expected 'no result found'", expt.Error())
	}
}
