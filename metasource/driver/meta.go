package driver

import (
	"encoding/xml"
	"fmt"
	"io"
	"metasource/metasource/models"
	"net/http"
	"strings"
	"time"
)

var ReadMetadata = func(unit *models.LinkUnit) ([]models.FileUnit, error) {
	mdlink := fmt.Sprintf("%s/repomd.xml", unit.Link)
	result := []models.FileUnit{}
	repomd := models.RepoMD{}

	rqst, expt := http.NewRequest("GET", mdlink, nil)
	if expt != nil {
		return result, expt
	}

	oper := &http.Client{Timeout: time.Second * 60}
	resp, expt := oper.Do(rqst)
	if expt != nil || resp.StatusCode != 200 {
		if expt != nil {
			return result, expt
		}
		if resp.StatusCode != 200 {
			return result, fmt.Errorf("%s", resp.Status)
		}
	}
	defer resp.Body.Close()

	body, expt := io.ReadAll(resp.Body)
	if expt != nil {
		return result, expt
	}

	expt = xml.Unmarshal(body, &repomd)
	if expt != nil {
		return result, expt
	}

	for _, item := range repomd.Data {
		if item.Type != "primary" && item.Type != "filelists" && item.Type != "other" {
			continue
		}

		if !strings.Contains(item.Location.Href, ".xml") {
			continue
		}

		name := strings.Replace(item.Location.Href, "repodata/", "", -1)
		path := fmt.Sprintf("%s/%s", unit.Link, name)
		hash := models.Checksum{Data: item.ChecksumOpen.Data, Type: item.ChecksumOpen.Type}
		file := models.FileUnit{Name: name, Path: path, Type: item.Type, Hash: hash, Keep: true}
		result = append(result, file)
	}

	return result, expt
}
