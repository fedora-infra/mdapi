package test

import (
	"errors"
	"fmt"
	"metasource/metasource/config"
	"metasource/metasource/driver"
	"metasource/metasource/models/home"
	"strings"
	"testing"
)

var filedict = map[string]home.FileUnit{
	"primary": {
		Keep: true,
		Name: "metasource-rawhide-primary.xml",
		Type: "primary",
		Path: "",
		Hash: home.Checksum{
			Data: "d69ef00db0cdfa189c4accae4ea0d2e4fc193b9a12f4d3db9d06ff9729d99808",
			Type: "sha256",
		},
	},
	"filelists": {
		Keep: true,
		Name: "metasource-rawhide-filelists.xml",
		Type: "filelists",
		Path: "",
		Hash: home.Checksum{
			Data: "3fc9351f8ed4f47662a2da87959120f4162b22c4c677638c77158ca49c475480",
			Type: "sha256",
		},
	},
	"other": {
		Keep: true,
		Name: "metasource-rawhide-other.xml",
		Type: "other",
		Path: "",
		Hash: home.Checksum{
			Data: "7a689d6ea74f2fe4271b872e097b4f00a896e3c05438b649f9bfaa4214240b94",
			Type: "sha256",
		},
	},
}

var repo = home.LinkUnit{
	Name: "rawhide",
	Link: "https://dl.fedoraproject.org/pub/fedora/linux/development/rawhide/Everything/x86_64/os/repodata/",
}

func WithMockedReadMetadata(t *testing.T, extn string) {
	t.Helper()

	host := "https://dl.fedoraproject.org/pub/fedora/linux/development/rawhide/Everything/x86_64/os/repodata"
	hash := "363d848c8459fa0b1e014bbf60cafada96312392ce48b8b018d5527c88cd5e50"
	original := driver.ReadMetadata
	driver.ReadMetadata = func(unit *home.LinkUnit) ([]home.FileUnit, error) {
		rslt := []home.FileUnit{
			{
				Keep: true,
				Name: fmt.Sprintf("%s-primary.xml.%s", hash, extn),
				Type: "primary",
				Path: fmt.Sprintf("%s/%s-primary.xml.%s", host, hash, extn),
				Hash: home.Checksum{Type: "sha256", Data: hash},
			},
			{
				Keep: true,
				Name: fmt.Sprintf("%s-filelists.xml.%s", hash, extn),
				Type: "filelists",
				Path: fmt.Sprintf("%s/%s-filelists.xml.%s", host, hash, extn),
				Hash: home.Checksum{Type: "sha256", Data: hash},
			},
			{
				Keep: true,
				Name: fmt.Sprintf("%s-other.xml.%s", hash, extn),
				Type: "other",
				Path: fmt.Sprintf("%s/%s-other.xml.%s", host, hash, extn),
				Hash: home.Checksum{Type: "sha256", Data: hash},
			},
		}
		return rslt, nil
	}

	t.Cleanup(func() {
		driver.ReadMetadata = original
	})
}

func WithMockedDownloadRepositories(t *testing.T, iden string, extn string) {
	t.Helper()

	original := driver.DownloadRepositories
	driver.DownloadRepositories = func(flut *home.FileUnit, vers *string, stab int64, cast *int, loca *string) error {
		for iter, data := range filedict {
			if strings.Contains(flut.Name, fmt.Sprintf("-%s.xml.%s", iter, extn)) {
				flut.Keep = data.Keep
				flut.Name = fmt.Sprintf("%s.%s", data.Name, extn)
				flut.Type = data.Type
				flut.Path = fmt.Sprintf("./assets/test-%s/%s", iden, flut.Name)
				flut.Hash = data.Hash
			}
		}
		*cast++
		return nil
	}

	t.Cleanup(func() {
		driver.DownloadRepositories = original
	})
}

func TestHandleRepositories_Success_XZ(t *testing.T) {
	iden := driver.GenerateIdentity(&config.RANDOM_LENGTH)

	Path_Archived_XZ(t, iden)
	WithMockedReadMetadata(t, "xz")
	WithMockedDownloadRepositories(t, iden, "xz")

	expt := driver.HandleRepositories(&repo)
	if expt != nil {
		t.Errorf("Received %s, Expected nothing", expt.Error())
	}
}

func TestHandleRepositories_Success_GZ(t *testing.T) {
	iden := driver.GenerateIdentity(&config.RANDOM_LENGTH)

	Path_Archived_GZ(t, iden)
	WithMockedReadMetadata(t, "gz")
	WithMockedDownloadRepositories(t, iden, "gz")

	expt := driver.HandleRepositories(&repo)
	if expt != nil {
		t.Errorf("Received %s, Expected nothing", expt.Error())
	}
}

func TestHandleRepositories_Success_ZSTD(t *testing.T) {
	iden := driver.GenerateIdentity(&config.RANDOM_LENGTH)

	Path_Archived_ZSTD(t, iden)
	WithMockedReadMetadata(t, "zst")
	WithMockedDownloadRepositories(t, iden, "zst")

	expt := driver.HandleRepositories(&repo)
	if expt != nil {
		t.Errorf("Received %s, Expected nothing", expt.Error())
	}
}

func TestHandleRepositories_Failure_ReadMetadata(t *testing.T) {
	iden := driver.GenerateIdentity(&config.RANDOM_LENGTH)

	Path_Archived_ZSTD(t, iden)
	WithMockedReadMetadata(t, "zst")
	WithMockedDownloadRepositories(t, iden, "zst")

	original := driver.ReadMetadata
	driver.ReadMetadata = func(unit *home.LinkUnit) ([]home.FileUnit, error) {
		return []home.FileUnit{}, errors.New("ReadMetadata failed")
	}
	defer func() {
		driver.ReadMetadata = original
	}()

	expt := driver.HandleRepositories(&repo)
	if expt == nil {
		t.Errorf("Received nil, Expected %s", "ReadMetadata failed")
	}
}

func TestHandleRepositories_Failure_InitPath(t *testing.T) {
	iden := driver.GenerateIdentity(&config.RANDOM_LENGTH)

	Path_Archived_ZSTD(t, iden)
	WithMockedReadMetadata(t, "zst")
	WithMockedDownloadRepositories(t, iden, "zst")

	original := driver.InitPath
	driver.InitPath = func(vers *string, loca *string) error {
		return errors.New("InitPath failed")
	}
	defer func() {
		driver.InitPath = original
	}()

	expt := driver.HandleRepositories(&repo)
	if expt == nil {
		t.Errorf("Received nil, Expected %s", "InitPath failed")
	}
}
