package test

import (
	"errors"
	"metasource/metasource/driver"
	"metasource/metasource/models"
	"metasource/metasource/option"
	"testing"
)

func TestDatabase_Failure_HandleRepositories(t *testing.T) {
	original := driver.HandleRepositories
	driver.HandleRepositories = func(unit *models.LinkUnit) error {
		return errors.New("HandleRepositories failed")
	}
	defer func() { driver.HandleRepositories = original }()

	expt := option.Database()
	if expt != nil {
		t.Errorf("Received '%s', Expected nothing", expt.Error())
	}
}

func TestDatabase_Failure_KillObsoleteBranches(t *testing.T) {
	originalHandle := driver.HandleRepositories
	driver.HandleRepositories = func(unit *models.LinkUnit) error {
		return errors.New("HandleRepositories failed")
	}
	defer func() { driver.HandleRepositories = originalHandle }()

	originalPurge := driver.KillObsoleteBranches
	driver.KillObsoleteBranches = func(active []models.LinkUnit) error {
		return errors.New("KillObsoleteBranches failed")
	}
	defer func() { driver.KillObsoleteBranches = originalPurge }()

	expt := option.Database()
	if expt != nil {
		t.Errorf("Received '%s', Expected nothing", expt.Error())
	}
}

func TestDatabase_Failure_PopulateRepositories(t *testing.T) {
	original := driver.PopulateRepositories
	driver.PopulateRepositories = func() ([]models.LinkUnit, error) {
		return []models.LinkUnit{}, errors.New("PopulateRepositories failed")
	}
	defer func() { driver.PopulateRepositories = original }()

	expt := option.Database()

	if expt == nil {
		t.Errorf("Received nothing, Expected error")
	} else if expt.Error() != "PopulateRepositories failed" {
		t.Errorf("Received '%s', Expected 'PopulateRepositories failed'", expt.Error())
	}
}
