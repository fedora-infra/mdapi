package test

import (
	"database/sql"
	"fmt"
	"metasource/metasource/config"
	"metasource/metasource/driver"
	"metasource/metasource/lookup"
	"metasource/metasource/models/home"
	"strings"
	"testing"
)

var vers_lookup_rela string = "rawhide"
var pack_lookup_rela home.PackUnit = home.PackUnit{
	Key:     1,
	Id:      sql.NullString{Valid: true, String: "28d3c752b8f7f78aae51fb4afee36d5bfdee295df85b3fdacb4bc0357f614784"},
	Name:    sql.NullString{Valid: true, String: "systemd"},
	Source:  sql.NullString{Valid: true, String: "systemd-257.5-6.fc42.src.rpm"},
	Epoch:   sql.NullString{Valid: true, String: "0"},
	Version: sql.NullString{Valid: true, String: "257.5"},
	Release: sql.NullString{Valid: true, String: "6.f42"},
	Arch:    sql.NullString{Valid: true, String: "i686"},
	Summary: sql.NullString{Valid: true, String: "System and Service Manager"},
	Desc:    sql.NullString{Valid: true, String: ""},
	Link:    sql.NullString{Valid: true, String: "https://systemd.io"},
}
var repo_lookup_rela string = "release"
var rela_lookup_rela string = "requires"

func TestReadRela_Failure_AbsentDB(t *testing.T) {
	original := config.DBFOLDER
	config.DBFOLDER = fmt.Sprintf("/var/tmp/test-%s", driver.GenerateIdentity(&config.RANDOM_LENGTH))
	defer func() { config.DBFOLDER = original }()

	_, expt := lookup.ReadRelation(&vers_lookup_rela, &pack_lookup_rela, &repo_lookup_rela, &rela_lookup_rela)
	if expt == nil {
		t.Errorf("Received nothing, Expected error")
	} else if !strings.Contains(expt.Error(), "no such file or directory") {
		t.Errorf("Received '%s', Expected 'stat /var/tmp/test-xxxxxxxx/metasource-xxxxxxxx-xxxxxxxx.sqlite: no such file or directory'", expt.Error())
	}
}

func TestReadRela_Failure_FaultyDB(t *testing.T) {
	Path_Init_Faulty(t)

	_, expt := lookup.ReadRelation(&vers_lookup_rela, &pack_lookup_rela, &repo_lookup_rela, &rela_lookup_rela)
	if expt == nil {
		t.Errorf("Received nothing, Expected error")
	} else if expt.Error() != "file is not a database" {
		t.Errorf("Received '%s', Expected 'file is not a database'", expt.Error())
	}
}

func TestReadRela_Failure_FaultyDriver(t *testing.T) {
	Path_Init(t, "")

	original := config.DBDRIVER
	config.DBDRIVER = "very-good-database-driver"
	defer func() { config.DBDRIVER = original }()

	_, expt := lookup.ReadRelation(&vers_lookup_rela, &pack_lookup_rela, &repo_lookup_rela, &rela_lookup_rela)
	if expt == nil {
		t.Errorf("Received nothing, Expected error")
	} else if expt.Error() != "sql: unknown driver \"very-good-database-driver\" (forgotten import?)" {
		t.Errorf("Received '%s', Expected 'sql: unknown driver \"very-good-database-driver\" (forgotten import?)'", expt.Error())
	}
}

func TestReadRela_Failure_FaultyPlea(t *testing.T) {
	Path_Init(t, "")

	original := config.OBTAIN_PACKAGE_BY
	config.OBTAIN_PACKAGE_BY = "SELECT p.name, p.arch FROM packages p JOIN %s t ON t.pkgKey = p.pkgKey WHERE t.name = ? ORDER BY p.epoch DESC, p.version DESC, p.release DESC"
	defer func() { config.OBTAIN_PACKAGE_BY = original }()

	_, expt := lookup.ReadRelation(&vers_lookup_rela, &pack_lookup_rela, &repo_lookup_rela, &rela_lookup_rela)
	if expt == nil {
		t.Errorf("Received nothing, Expected error")
	} else if expt.Error() != "sql: expected 2 destination arguments in Scan, not 11" {
		t.Errorf("Received '%s', Expected 'sql: expected 2 destination arguments in Scan, not 11'", expt.Error())
	}
}
