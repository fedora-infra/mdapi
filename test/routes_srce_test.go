package test

import (
	"encoding/json"
	"errors"
	"metasource/metasource/lookup"
	"metasource/metasource/models/dict"
	"metasource/metasource/models/home"
	"metasource/metasource/option"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestSrce_Init_FromName_Success(t *testing.T) {
	Path_Init(t, "")

	router := option.Navigate()
	rqster := httptest.NewRequest("GET", "/rawhide/srcpkg/systemd", nil)
	record := httptest.NewRecorder()
	router.ServeHTTP(record, rqster)

	if !strings.Contains(record.Header().Get("content-type"), "application/json") {
		t.Errorf("Received %s, Expected %s", record.Header().Get("content-type"), "application/json")
	}

	rslt := dict.UnitPrimary{}
	expt := json.Unmarshal(record.Body.Bytes(), &rslt)
	if expt != nil {
		t.Errorf("Unable to unmarshal JSON")
	}

	if record.Code != http.StatusOK {
		t.Errorf("Received %d, Expected %d", record.Code, http.StatusOK)
	}
}

func TestSrce_Init_FromSrce_Success(t *testing.T) {
	Path_Init(t, "")

	router := option.Navigate()
	rqster := httptest.NewRequest("GET", "/rawhide/srcpkg/systemd-boot-unsigned-sourcepack", nil)
	record := httptest.NewRecorder()
	router.ServeHTTP(record, rqster)

	if !strings.Contains(record.Header().Get("content-type"), "application/json") {
		t.Errorf("Received %s, Expected %s", record.Header().Get("content-type"), "application/json")
	}

	rslt := dict.UnitPrimary{}
	expt := json.Unmarshal(record.Body.Bytes(), &rslt)
	if expt != nil {
		t.Errorf("Unable to unmarshal JSON")
	}

	if record.Code != http.StatusOK {
		t.Errorf("Received %d, Expected %d", record.Code, http.StatusOK)
	}
}

func TestSrce_Init_Failure_AbsentVers_C400(t *testing.T) {
	Path_UnInit(t, "/var/tmp")

	router := option.Navigate()
	rqster := httptest.NewRequest("GET", "//srcpkg/systemd", nil)
	record := httptest.NewRecorder()
	router.ServeHTTP(record, rqster)

	if !strings.Contains(record.Header().Get("content-type"), "text/plain") {
		t.Errorf("Received %s, Expected %s", record.Header().Get("content-type"), "text/plain")
	}

	if record.Code != http.StatusBadRequest {
		t.Errorf("Received %d, Expected %d", record.Code, http.StatusBadRequest)
	}
}

func TestSrce_Init_Failure_ReadSrce_Misc_C400(t *testing.T) {
	Path_UnInit(t, "/var/tmp")

	original := lookup.ReadSrce
	lookup.ReadSrce = func(vers *string, name *string) (home.PackUnit, string, error) {
		return home.PackUnit{}, "", errors.New("ReadSrce failed")
	}
	defer func() { lookup.ReadSrce = original }()

	router := option.Navigate()
	rqster := httptest.NewRequest("GET", "/rawhide/srcpkg/systemd", nil)
	record := httptest.NewRecorder()
	router.ServeHTTP(record, rqster)

	if !strings.Contains(record.Header().Get("content-type"), "text/plain") {
		t.Errorf("Received %s, Expected %s", record.Header().Get("content-type"), "text/plain")
	}

	if record.Code != http.StatusBadRequest {
		t.Errorf("Received %d, Expected %d", record.Code, http.StatusBadRequest)
	}
}

func TestSrce_Init_Failure_ReadSrce_Lost_C404(t *testing.T) {
	Path_UnInit(t, "/var/tmp")

	original := lookup.ReadSrce
	lookup.ReadSrce = func(vers *string, name *string) (home.PackUnit, string, error) {
		return home.PackUnit{}, "", errors.New("no result found")
	}
	defer func() { lookup.ReadSrce = original }()

	router := option.Navigate()
	rqster := httptest.NewRequest("GET", "/rawhide/srcpkg/systemd", nil)
	record := httptest.NewRecorder()
	router.ServeHTTP(record, rqster)

	if !strings.Contains(record.Header().Get("content-type"), "text/plain") {
		t.Errorf("Received %s, Expected %s", record.Header().Get("content-type"), "text/plain")
	}

	if record.Code != http.StatusNotFound {
		t.Errorf("Received %d, Expected %d", record.Code, http.StatusNotFound)
	}
}

func TestSrce_Init_Failure_ReadExtn_Misc_C400(t *testing.T) {
	Path_Init(t, "")

	original := lookup.ReadExtn
	lookup.ReadExtn = func(vers *string, pack *home.PackUnit, repo *string) (home.ExtnUnit, error) {
		return home.ExtnUnit{}, errors.New("ReadExtn failed")
	}
	defer func() { lookup.ReadExtn = original }()

	router := option.Navigate()
	rqster := httptest.NewRequest("GET", "/rawhide/srcpkg/systemd", nil)
	record := httptest.NewRecorder()
	router.ServeHTTP(record, rqster)

	if !strings.Contains(record.Header().Get("content-type"), "text/plain") {
		t.Errorf("Received %s, Expected %s", record.Header().Get("content-type"), "text/plain")
	}

	if record.Code != http.StatusBadRequest {
		t.Errorf("Received %d, Expected %d", record.Code, http.StatusBadRequest)
	}
}

func TestSrce_Init_Failure_ReadCoop_Misc_C400(t *testing.T) {
	Path_Init(t, "")

	origextn := lookup.ReadExtn
	lookup.ReadExtn = func(vers *string, pack *home.PackUnit, repo *string) (home.ExtnUnit, error) {
		return home.ExtnUnit{}, nil
	}
	defer func() { lookup.ReadExtn = origextn }()

	origcoop := lookup.ReadCoop
	lookup.ReadCoop = func(vers *string, pack *home.PackUnit, repo *string) ([]string, error) {
		return []string{}, errors.New("ReadCoop failed")
	}
	defer func() { lookup.ReadCoop = origcoop }()

	router := option.Navigate()
	rqster := httptest.NewRequest("GET", "/rawhide/srcpkg/systemd", nil)
	record := httptest.NewRecorder()
	router.ServeHTTP(record, rqster)

	if !strings.Contains(record.Header().Get("content-type"), "text/plain") {
		t.Errorf("Received %s, Expected %s", record.Header().Get("content-type"), "text/plain")
	}

	if record.Code != http.StatusBadRequest {
		t.Errorf("Received %d, Expected %d", record.Code, http.StatusBadRequest)
	}
}

func TestSrce_Init_Failure_AbsentName_C404(t *testing.T) {
	Path_UnInit(t, "/var/tmp")

	router := option.Navigate()
	rqster := httptest.NewRequest("GET", "/rawhide/srcpkg/", nil)
	record := httptest.NewRecorder()
	router.ServeHTTP(record, rqster)

	if !strings.Contains(record.Header().Get("content-type"), "text/plain") {
		t.Errorf("Received %s, Expected %s", record.Header().Get("content-type"), "text/plain")
	}

	if record.Code != http.StatusNotFound {
		t.Errorf("Received %d, Expected %d", record.Code, http.StatusNotFound)
	}
}
