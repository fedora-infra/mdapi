package test

import (
	"fmt"
	"metasource/metasource/config"
	"metasource/metasource/driver"
	"metasource/metasource/models/home"
	"sync"
	"testing"
)

func TestWithdrawArchives_Failure_AbsentSrce(t *testing.T) {
	wait := sync.WaitGroup{}
	brch, loca := "rawhide", "absent-folder"
	castup, entire := 0, 3
	tempdict := map[string]home.FileUnit{}
	for iter, unit := range filedict {
		tempdict[iter] = unit
	}

	for _, unit := range tempdict {
		wait.Add(1)
		go driver.WithdrawArchives(&unit, &brch, &wait, &castup, &loca)
	}
	wait.Wait()

	if castup == entire {
		t.Errorf("Received %d, Expected %d", 0, entire)
	}
}

func TestWithdrawArchives_Failure_AbsentDest(t *testing.T) {
	iden := driver.GenerateIdentity(&config.RANDOM_LENGTH)
	Path_Archived_ZSTD(t, iden)

	wait := sync.WaitGroup{}
	brch, loca := "rawhide", config.DBFOLDER
	castup, entire := 0, 3

	for _, unit := range filedict {
		wait.Add(1)
		unit.Path = fmt.Sprintf("%s/%s", config.DBFOLDER, fmt.Sprintf("%s.zst", unit.Name))
		unit.Name = fmt.Sprintf("mistaken-%s.zst", unit.Name)
		go driver.WithdrawArchives(&unit, &brch, &wait, &castup, &loca)
	}
	wait.Wait()

	if castup == entire {
		t.Errorf("Received %d, Expected %d", 0, entire)
	}
}

func TestWithdrawArchives_Failure_FaultyFile(t *testing.T) {
	for _, extn := range []string{"zst", "xz", "gz"} {
		iden := driver.GenerateIdentity(&config.RANDOM_LENGTH)
		Path_Archived_FaultyFile(t, iden, extn)

		wait := sync.WaitGroup{}
		brch, loca := "rawhide", config.DBFOLDER
		castup, entire := 0, 3

		for _, unit := range filedict {
			wait.Add(1)
			unit.Path = fmt.Sprintf("%s/%s", config.DBFOLDER, fmt.Sprintf("%s.%s", unit.Name, extn))
			unit.Name = fmt.Sprintf("%s.%s", unit.Name, extn)
			go driver.WithdrawArchives(&unit, &brch, &wait, &castup, &loca)
		}
		wait.Wait()

		if castup == entire {
			t.Errorf("Received %d, Expected %d", 0, entire)
		}
	}
}
