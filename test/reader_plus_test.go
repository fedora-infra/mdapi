package test

import (
	"fmt"
	"metasource/metasource/config"
	"metasource/metasource/driver"
	"metasource/metasource/reader"
	"os"
	"testing"
)

func TestMakeDatabaseSuccess(t *testing.T) {
	vers := "testbase"
	cast := 0
	basepath := "./assets"
	destpath := fmt.Sprintf("%s/test-%s", basepath, driver.GenerateIdentity(&config.RANDOM_LENGTH))
	expt := os.MkdirAll(destpath, 0755)
	if expt != nil {
		t.Errorf("Database generation failed")
	}

	prmyinpt := fmt.Sprintf("%s/%s", basepath, "testbase_primary.xml")
	fileinpt := fmt.Sprintf("%s/%s", basepath, "testbase_filelists.xml")
	othrinpt := fmt.Sprintf("%s/%s", basepath, "testbase_other.xml")
	prmyname := "testbase_primary.sqlite"
	filename := "testbase_filelists.sqlite"
	othrname := "testbase_other.sqlite"
	prmypath := fmt.Sprintf("%s/%s", destpath, prmyname)
	filepath := fmt.Sprintf("%s/%s", destpath, filename)
	othrpath := fmt.Sprintf("%s/%s", destpath, othrname)

	defer WipeGeneration(destpath)

	expected := 27
	packages, expt := reader.MakeDatabase(&vers, &cast, &prmyinpt, &fileinpt, &othrinpt, &prmyname, &filename, &othrname, &prmypath, &filepath, &othrpath)

	if packages != expected {
		t.Errorf("Received %d, Expected %d", packages, expected)
	}

	if expt != nil {
		t.Errorf("Received %s, Expected nothing", expt.Error())
	}
}

func TestMakeDatabaseFailureAAAA(t *testing.T) {
	vers := "testbase"
	cast := 0
	basepath := "./assets"
	destpath := fmt.Sprintf("%s/test-%s", basepath, driver.GenerateIdentity(&config.RANDOM_LENGTH))
	expt := os.MkdirAll(destpath, 0755)
	if expt != nil {
		t.Errorf("Database generation failed")
	}

	prmyinpt := fmt.Sprintf("%s/%s", basepath, "testbase_absent_primary.xml")
	fileinpt := fmt.Sprintf("%s/%s", basepath, "testbase_absent_filelists.xml")
	othrinpt := fmt.Sprintf("%s/%s", basepath, "testbase_absent_other.xml")
	prmyname := "testbase_primary.sqlite"
	filename := "testbase_filelists.sqlite"
	othrname := "testbase_other.sqlite"
	prmypath := fmt.Sprintf("%s/%s", destpath, prmyname)
	filepath := fmt.Sprintf("%s/%s", destpath, filename)
	othrpath := fmt.Sprintf("%s/%s", destpath, othrname)

	defer WipeGeneration(destpath)

	expected := 0
	packages, expt := reader.MakeDatabase(&vers, &cast, &prmyinpt, &fileinpt, &othrinpt, &prmyname, &filename, &othrname, &prmypath, &filepath, &othrpath)

	if packages != expected {
		t.Errorf("Received %d, Expected %d", packages, expected)
	}

	if expt == nil {
		t.Errorf("Received nothing, Expected error")
	} else if expt.Error() != "Cannot open ./assets/testbase_absent_primary.xml: File ./assets/testbase_absent_primary.xml doesn't exist or not a regular file" {
		t.Errorf("Received '%s', Expected 'Cannot open ./assets/testbase_absent_primary.xml: File ./assets/testbase_absent_primary.xml doesn't exist or not a regular file'", expt.Error())
	}
}

func TestMakeDatabaseFailureBBBB(t *testing.T) {
	vers := "testbase"
	cast := 0
	basepath := "./assets"
	destpath := fmt.Sprintf("%s/test-%s", basepath, driver.GenerateIdentity(&config.RANDOM_LENGTH))
	expt := os.MkdirAll(destpath, 0755)
	if expt != nil {
		t.Errorf("Database generation failed")
	}

	prmyinpt := fmt.Sprintf("%s/%s", basepath, "testbase_primary.xml")
	fileinpt := fmt.Sprintf("%s/%s", basepath, "testbase_filelists.xml")
	othrinpt := fmt.Sprintf("%s/%s", basepath, "testbase_other.xml")
	prmyname := "testbase_primary.sqlite"
	filename := "testbase_filelists.sqlite"
	othrname := "testbase_other.sqlite"
	prmypath := fmt.Sprintf("%s/%s", destpath, prmyname)
	filepath := fmt.Sprintf("%s/%s", destpath, filename)
	othrpath := fmt.Sprintf("%s/%s", destpath, othrname)

	prmyback := fmt.Sprintf("%s/%s", basepath, prmyname)
	fileback := fmt.Sprintf("%s/%s", basepath, filename)
	othrback := fmt.Sprintf("%s/%s", basepath, othrname)
	_ = CopyGeneration(prmyback, prmypath)
	_ = CopyGeneration(fileback, filepath)
	_ = CopyGeneration(othrback, othrpath)
	defer WipeGeneration(destpath)

	expected := 0
	packages, expt := reader.MakeDatabase(&vers, &cast, &prmyinpt, &fileinpt, &othrinpt, &prmyname, &filename, &othrname, &prmypath, &filepath, &othrpath)

	if packages != expected {
		t.Errorf("Received %d, Expected %d", packages, expected)
	}

	if expt == nil {
		t.Errorf("Received nil, Expected %s", "metadata databases already exist or opening failed")
	}
}
