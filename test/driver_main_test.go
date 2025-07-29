package test

import (
	"errors"
	"metasource/metasource/driver"
	"metasource/metasource/models/home"
	"metasource/metasource/option"
	"testing"
)

func TestDatabase_Failure_HandleRepositories(t *testing.T) {
	original := driver.HandleRepositories
	driver.HandleRepositories = func(unit *home.LinkUnit) error {
		return errors.New("HandleRepositories failed")
	}
	defer func() { driver.HandleRepositories = original }()

	expt := option.Database()
	if expt != nil {
		t.Errorf("Received '%s', Expected nothing", expt.Error())
	}
}

func TestDatabase_Failure_PopulateRepositories(t *testing.T) {
	original := driver.PopulateRepositories
	driver.PopulateRepositories = func() ([]home.LinkUnit, error) {
		return []home.LinkUnit{}, errors.New("PopulateRepositories failed")
	}
	defer func() { driver.PopulateRepositories = original }()

	expt := option.Database()

	if expt == nil {
		t.Errorf("Received nothing, Expected error")
	} else if expt.Error() != "PopulateRepositories failed" {
		t.Errorf("Received '%s', Expected 'PopulateRepositories failed'", expt.Error())
	}
}
