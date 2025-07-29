package test

import (
	"metasource/metasource/config"
	"metasource/metasource/driver"
	"metasource/metasource/models/home"
	"testing"
)

func TestDownload_Success(t *testing.T) {
	Path_Init_Vacant(t)

	unit := home.LinkUnit{
		Name: "rawhide",
		Link: "https://dl.fedoraproject.org/pub/fedora/linux/development/rawhide/Everything/x86_64/os/repodata/",
	}

	list, expt := driver.ReadMetadata(&unit)
	if expt != nil {
		t.Errorf("Test requires active internet connection")
	}
	if len(list) != 3 {
		t.Errorf("Received %d, Expected %d", len(list), 3)
	}

	castup, entire := 0, 3
	for indx := range list {
		expt = driver.DownloadRepositories(&list[indx], &unit.Name, 0, &castup, &config.DBFOLDER)
		if expt != nil {
			t.Errorf("Test requires active internet connection")
		}
	}

	if castup != entire {
		t.Errorf("Received %d, Expected %d", castup, entire)
	}
}

func TestDownload_FailureStabOverflow(t *testing.T) {
	Path_Init_Vacant(t)

	unit := home.LinkUnit{
		Name: "rawhide",
		Link: "https://dl.fedoraproject.org/pub/fedora/linux/development/rawhide/Everything/x86_64/os/repodata/",
	}

	list, expt := driver.ReadMetadata(&unit)
	if expt != nil {
		t.Errorf("Test requires active internet connection")
	}
	if len(list) != 3 {
		t.Errorf("Received %d, Expected %d", len(list), 3)
	}

	castup, stab := 0, config.ATTEMPTS
	for indx := range list {
		expt = driver.DownloadRepositories(&list[indx], &unit.Name, stab, &castup, &config.DBFOLDER)
		if expt == nil {
			t.Errorf("Received nil, Expected %s", "most attempts failed")
		} else if expt.Error() != "most attempts failed" {
			t.Errorf("Received '%s', Expected 'most attempts failed'", expt.Error())
		}
	}
}

func TestDownload_FailureMistakenPath(t *testing.T) {
	Path_Init_Vacant(t)

	unit := home.LinkUnit{
		Name: "rawhide",
		Link: "https://dl.fedoraproject.org/pub/fedora/linux/development/rawhide/Everything/x86_64/os/repodata/",
	}

	list, expt := driver.ReadMetadata(&unit)
	if expt != nil {
		t.Errorf("Test requires active internet connection")
	}
	if len(list) != 3 {
		t.Errorf("Received %d, Expected %d", len(list), 3)
	}

	castup, path := 0, "/nonexistent"
	for indx := range list {
		_ = driver.DownloadRepositories(&list[indx], &unit.Name, 0, &castup, &path)
	}

	castup, stab := 0, config.ATTEMPTS
	for indx := range list {
		expt = driver.DownloadRepositories(&list[indx], &unit.Name, stab, &castup, &config.DBFOLDER)
		if expt == nil {
			t.Errorf("Received nil, Expected %s", "most attempts failed")
		} else if expt.Error() != "most attempts failed" {
			t.Errorf("Received '%s', Expected 'most attempts failed'", expt.Error())
		}
	}
}

func TestDownload_FailureMistakenLink_Prep(t *testing.T) {
	Path_Init_Vacant(t)

	var expt error

	unit := home.LinkUnit{
		Name: "rawhide",
		Link: "https://dl.fedoraproject.org/pub/fedora/linux/development/rawhide/Everything/x86_64/os/repodata/",
	}

	list := []home.FileUnit{
		home.FileUnit{
			Name: "c26498749f2ea9d456cf64f7ab1ce276e241d327fa8377002c38eeace1470d97-primary.xml.zst",
			Path: "flaw//\x7f,link/pub/fedora/linux/development/rawhide/Everything/x86_64/os/repodata/c26498749f2ea9d456cf64f7ab1ce276e241d327fa8377002c38eeace1470d97-primary.xml.zst",
			Type: "primary",
			Hash: home.Checksum{
				Data: "0f8fe582dc9e2bf301db59dcb9310f92019e2004f271be13be21543e3350b6b8",
				Type: "sha256",
			},
			Keep: true,
		},
		home.FileUnit{
			Name: "37b1ecdb03a7f077d547eb3decdda898e205b94b431730c713cc768b89a58413-filelists.xml.zst",
			Path: "flaw//\x7f,link/pub/fedora/linux/development/rawhide/Everything/x86_64/os/repodata/37b1ecdb03a7f077d547eb3decdda898e205b94b431730c713cc768b89a58413-filelists.xml.zst",
			Type: "filelists",
			Hash: home.Checksum{
				Data: "8134c2d80f175bb95a3f50c592f6201bdadca7cf830ae672aa935530e6c65a4d",
				Type: "sha256",
			},
			Keep: true,
		},
		home.FileUnit{
			Name: "fd7cf8e2dec5ae494374323e136a478f3cc706cfbf9a7b54afc13dbbaa2935c0-other.xml.zst",
			Path: "flaw//\x7f,link/pub/fedora/linux/development/rawhide/Everything/x86_64/os/repodata/fd7cf8e2dec5ae494374323e136a478f3cc706cfbf9a7b54afc13dbbaa2935c0-other.xml.zst",
			Type: "other",
			Hash: home.Checksum{
				Data: "16e4194cc8c1818113fb4e6e3d2af154fa7ee06384ec7fbaa1ce5a92ce7ef01d",
				Type: "sha256",
			},
			Keep: true,
		},
	}

	castup, path := 0, "/nonexistent"
	for indx := range list {
		_ = driver.DownloadRepositories(&list[indx], &unit.Name, 0, &castup, &path)
	}

	castup = 0
	for indx := range list {
		expt = driver.DownloadRepositories(&list[indx], &unit.Name, 0, &castup, &config.DBFOLDER)
		if expt == nil {
			t.Errorf("Received nil, Expected %s", "most attempts failed")
		} else if expt.Error() != "most attempts failed" {
			t.Errorf("Received '%s', Expected 'most attempts failed'", expt.Error())
		}
	}
}

func TestDownload_FailureMistakenLink_Oper(t *testing.T) {
	Path_Init_Vacant(t)

	var expt error

	unit := home.LinkUnit{
		Name: "rawhide",
		Link: "https://dl.fedoraproject.org/pub/fedora/linux/development/rawhide/Everything/x86_64/os/repodata/",
	}

	list := []home.FileUnit{
		home.FileUnit{
			Name: "c26498749f2ea9d456cf64f7ab1ce276e241d327fa8377002c38eeace1470d97-primary.xml.zst",
			Path: "flaw://mistaken.link/pub/fedora/linux/development/rawhide/Everything/x86_64/os/repodata/c26498749f2ea9d456cf64f7ab1ce276e241d327fa8377002c38eeace1470d97-primary.xml.zst",
			Type: "primary",
			Hash: home.Checksum{
				Data: "0f8fe582dc9e2bf301db59dcb9310f92019e2004f271be13be21543e3350b6b8",
				Type: "sha256",
			},
			Keep: true,
		},
		home.FileUnit{
			Name: "37b1ecdb03a7f077d547eb3decdda898e205b94b431730c713cc768b89a58413-filelists.xml.zst",
			Path: "flaw://mistaken.link/pub/fedora/linux/development/rawhide/Everything/x86_64/os/repodata/37b1ecdb03a7f077d547eb3decdda898e205b94b431730c713cc768b89a58413-filelists.xml.zst",
			Type: "filelists",
			Hash: home.Checksum{
				Data: "8134c2d80f175bb95a3f50c592f6201bdadca7cf830ae672aa935530e6c65a4d",
				Type: "sha256",
			},
			Keep: true,
		},
		home.FileUnit{
			Name: "fd7cf8e2dec5ae494374323e136a478f3cc706cfbf9a7b54afc13dbbaa2935c0-other.xml.zst",
			Path: "flaw://mistaken.link/pub/fedora/linux/development/rawhide/Everything/x86_64/os/repodata/fd7cf8e2dec5ae494374323e136a478f3cc706cfbf9a7b54afc13dbbaa2935c0-other.xml.zst",
			Type: "other",
			Hash: home.Checksum{
				Data: "16e4194cc8c1818113fb4e6e3d2af154fa7ee06384ec7fbaa1ce5a92ce7ef01d",
				Type: "sha256",
			},
			Keep: true,
		},
	}

	castup, path := 0, "/nonexistent"
	for indx := range list {
		_ = driver.DownloadRepositories(&list[indx], &unit.Name, 0, &castup, &path)
	}

	castup = 0
	for indx := range list {
		expt = driver.DownloadRepositories(&list[indx], &unit.Name, 0, &castup, &config.DBFOLDER)
		if expt == nil {
			t.Errorf("Received nil, Expected %s", "most attempts failed")
		} else if expt.Error() != "most attempts failed" {
			t.Errorf("Received '%s', Expected 'most attempts failed'", expt.Error())
		}
	}
}
