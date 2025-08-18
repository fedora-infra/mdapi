package test

import (
	"fmt"
	"metasource/metasource/config"
	"metasource/metasource/driver"
	"metasource/metasource/lookup"
	"strings"
	"testing"
)

func TestReadBranches_Failure(t *testing.T) {
	original := config.DBFOLDER
	config.DBFOLDER = fmt.Sprintf("/var/tmp/test-%s", driver.GenerateIdentity(&config.RANDOM_LENGTH))
	defer func() { config.DBFOLDER = original }()

	_, expt := lookup.ReadBranches()
	if expt == nil {
		t.Errorf("Received nothing, Expected error")
	} else if !strings.Contains(expt.Error(), "no such file or directory") {
		t.Errorf("Received '%s', Expected 'open /var/tmp/test-xxxxxxxx: no such file or directory'", expt.Error())
	}
}

func TestInsertBranch_Repeat(t *testing.T) {
	rslt := []string{
		"metasource-rawhide-filelists.sqlite",
		"metasource-rawhide-other.sqlite",
		"metasource-rawhide-primary.sqlite",
	}

	list := []string{
		"metasource-rawhide-filelists.sqlite",
		"metasource-rawhide-other.sqlite",
		"metasource-rawhide-primary.sqlite",
		"metasource-src_rawhide-filelists.sqlite",
		"metasource-src_rawhide-other.sqlite",
		"metasource-src_rawhide-primary.sqlite",
	}

	for _, item := range list {
		lookup.InsertBranch(&rslt, &item)
	}

	for iter := range list {
		if rslt[iter] != list[iter] {
			t.Errorf("Received %s, Expected %s", rslt[iter], list[iter])
		}
	}
}
