package test

import (
	"encoding/json"
	"errors"
	"metasource/metasource/lookup"
	"metasource/metasource/models"
	"metasource/metasource/option"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestFile_Init_Success(t *testing.T) {
	Path_Init(t, "")

	router := option.Navigate()
	rqster := httptest.NewRequest("GET", "/rawhide/files/systemd", nil)
	record := httptest.NewRecorder()
	router.ServeHTTP(record, rqster)

	if !strings.Contains(record.Header().Get("content-type"), "application/json") {
		t.Errorf("Received %s, Expected %s", record.Header().Get("content-type"), "application/json")
	}

	rslt := models.UnitFileList{}
	expt := json.Unmarshal(record.Body.Bytes(), &rslt)
	if expt != nil {
		t.Errorf("Unable to unmarshal JSON")
	}

	if record.Code != http.StatusOK {
		t.Errorf("Received %d, Expected %d", record.Code, http.StatusOK)
	}
}

func TestFile_Init_Success_Updates(t *testing.T) {
	Path_Init(t, "updates")

	router := option.Navigate()
	rqster := httptest.NewRequest("GET", "/rawhide/files/systemd", nil)
	record := httptest.NewRecorder()
	router.ServeHTTP(record, rqster)

	if !strings.Contains(record.Header().Get("content-type"), "application/json") {
		t.Errorf("Received %s, Expected %s", record.Header().Get("content-type"), "application/json")
	}

	rslt := models.UnitOther{}
	expt := json.Unmarshal(record.Body.Bytes(), &rslt)
	if expt != nil {
		t.Errorf("Unable to unmarshal JSON")
	}

	if record.Code != http.StatusOK {
		t.Errorf("Received %d, Expected %d", record.Code, http.StatusOK)
	}
}

func TestFile_Init_Failure_AbsentVers_C400(t *testing.T) {
	Path_UnInit(t, "/var/tmp")

	router := option.Navigate()
	rqster := httptest.NewRequest("GET", "//files/systemd", nil)
	record := httptest.NewRecorder()
	router.ServeHTTP(record, rqster)

	if !strings.Contains(record.Header().Get("content-type"), "text/plain") {
		t.Errorf("Received %s, Expected %s", record.Header().Get("content-type"), "text/plain")
	}

	if record.Code != http.StatusBadRequest {
		t.Errorf("Received %d, Expected %d", record.Code, http.StatusBadRequest)
	}
}

func TestFile_Init_Failure_ReadPrmy_Misc_C400(t *testing.T) {
	Path_UnInit(t, "/var/tmp")

	original := lookup.ReadPrmy
	lookup.ReadPrmy = func(vers *string, name *string) (models.PackUnit, string, error) {
		return models.PackUnit{}, "", errors.New("ReadPrmy failed")
	}
	defer func() { lookup.ReadPrmy = original }()

	router := option.Navigate()
	rqster := httptest.NewRequest("GET", "/rawhide/files/systemd", nil)
	record := httptest.NewRecorder()
	router.ServeHTTP(record, rqster)

	if !strings.Contains(record.Header().Get("content-type"), "text/plain") {
		t.Errorf("Received %s, Expected %s", record.Header().Get("content-type"), "text/plain")
	}

	if record.Code != http.StatusBadRequest {
		t.Errorf("Received %d, Expected %d", record.Code, http.StatusBadRequest)
	}
}

func TestFile_Init_Failure_ReadPrmy_Lost_C404(t *testing.T) {
	Path_UnInit(t, "/var/tmp")

	original := lookup.ReadPrmy
	lookup.ReadPrmy = func(vers *string, name *string) (models.PackUnit, string, error) {
		return models.PackUnit{}, "", errors.New("no result found")
	}
	defer func() { lookup.ReadPrmy = original }()

	router := option.Navigate()
	rqster := httptest.NewRequest("GET", "/rawhide/files/systemd", nil)
	record := httptest.NewRecorder()
	router.ServeHTTP(record, rqster)

	if !strings.Contains(record.Header().Get("content-type"), "text/plain") {
		t.Errorf("Received %s, Expected %s", record.Header().Get("content-type"), "text/plain")
	}

	if record.Code != http.StatusNotFound {
		t.Errorf("Received %d, Expected %d", record.Code, http.StatusNotFound)
	}
}

func TestFile_Init_Failure_ReadFile_Misc_C400(t *testing.T) {
	Path_Init(t, "")

	original := lookup.ReadFile
	lookup.ReadFile = func(vers *string, pack *models.PackUnit, repo *string) (models.FilelistRslt, error) {
		return models.FilelistRslt{}, errors.New("ReadFile failed")
	}
	defer func() { lookup.ReadFile = original }()

	router := option.Navigate()
	rqster := httptest.NewRequest("GET", "/rawhide/files/systemd", nil)
	record := httptest.NewRecorder()
	router.ServeHTTP(record, rqster)

	if !strings.Contains(record.Header().Get("content-type"), "text/plain") {
		t.Errorf("Received %s, Expected %s", record.Header().Get("content-type"), "text/plain")
	}

	if record.Code != http.StatusBadRequest {
		t.Errorf("Received %d, Expected %d", record.Code, http.StatusBadRequest)
	}
}

func TestFile_Init_Failure_AbsentName_C404(t *testing.T) {
	Path_UnInit(t, "/var/tmp")

	router := option.Navigate()
	rqster := httptest.NewRequest("GET", "/rawhide/files/", nil)
	record := httptest.NewRecorder()
	router.ServeHTTP(record, rqster)

	if !strings.Contains(record.Header().Get("content-type"), "text/plain") {
		t.Errorf("Received %s, Expected %s", record.Header().Get("content-type"), "text/plain")
	}

	if record.Code != http.StatusNotFound {
		t.Errorf("Received %d, Expected %d", record.Code, http.StatusNotFound)
	}
}
