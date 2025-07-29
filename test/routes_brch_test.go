package test

import (
	"errors"
	"metasource/metasource/lookup"
	"metasource/metasource/option"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestBranches_Init_Success(t *testing.T) {
	Path_Init(t, "")

	router := option.Navigate()
	rqster := httptest.NewRequest("GET", "/branches", nil)
	record := httptest.NewRecorder()
	router.ServeHTTP(record, rqster)

	if !strings.Contains(record.Header().Get("content-type"), "application/json") {
		t.Errorf("Received %s, Expected %s", record.Header().Get("content-type"), "application/json")
	}

	if record.Body.String() != "[\"rawhide\"]\n" {
		t.Errorf("Received %s, Expected %s", record.Body.String(), "[\"rawhide\"]")
	}

	if record.Code != http.StatusOK {
		t.Errorf("Received %d, Expected %d", record.Code, http.StatusOK)
	}
}

func TestBranches_UnInit_Success(t *testing.T) {
	Path_UnInit(t, "/var/tmp")

	router := option.Navigate()
	rqster := httptest.NewRequest("GET", "/branches", nil)
	record := httptest.NewRecorder()
	router.ServeHTTP(record, rqster)

	if !strings.Contains(record.Header().Get("content-type"), "application/json") {
		t.Errorf("Received %s, Expected %s", record.Header().Get("content-type"), "application/json")
	}

	if record.Body.String() != "[]\n" {
		t.Errorf("Received %s, Expected %s", record.Body.String(), "[]")
	}

	if record.Code != http.StatusOK {
		t.Errorf("Received %d, Expected %d", record.Code, http.StatusOK)
	}
}

func TestBranches_UnInit_Failure(t *testing.T) {
	Path_UnInit(t, "/var/tmp")

	router := option.Navigate()
	rqster := httptest.NewRequest("GET", "/branches", nil)
	record := httptest.NewRecorder()

	original := lookup.ReadBranches
	lookup.ReadBranches = func() ([]string, error) {
		return []string{}, errors.New("ReadBranches failed")
	}
	defer func() { lookup.ReadBranches = original }()

	router.ServeHTTP(record, rqster)

	if !strings.Contains(record.Header().Get("content-type"), "text/plain") {
		t.Errorf("Received %s, Expected %s", record.Header().Get("content-type"), "text/plain")
	}

	if record.Body.String() != "500: Internal Server Error\n" {
		t.Errorf("Received %s, Expected %s", record.Body.String(), "500: Internal Server Error")
	}

	if record.Code != http.StatusInternalServerError {
		t.Errorf("Received %d, Expected %d", record.Code, http.StatusInternalServerError)
	}
}
