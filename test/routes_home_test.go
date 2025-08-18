package test

import (
	"errors"
	"metasource/metasource/lookup"
	"metasource/metasource/option"
	"metasource/metasource/routes"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestHome_UnInit_Success(t *testing.T) {
	Path_UnInit(t, "/var/tmp")

	router := option.Navigate()
	rqster := httptest.NewRequest("GET", "/", nil)
	record := httptest.NewRecorder()
	router.ServeHTTP(record, rqster)

	subslist := []string{
		"MetaSource is a performant source for RPM repositories metadata which ",
		"has an access to the metadata of the different Fedora Linux package ",
		"repositories and will serve you the most recent information available.",
		"It will parse through the \"updates-testing\" repository before moving",
		"onto the likes of \"updates\" and \"releases\" repository if no ",
		"information is found in the previous repository.",
		"Utilize the fast lookup interface to acquaint yourself with the API ",
		"endpoints and expected outputs. Press ENTER after typing the name to ",
		"execute a lookup in a new window. If you query for a non-existent ",
		"branch - it will return an HTTP 400 error. If you query for a ",
		"non-existent package - it will return an HTTP 404 error. Please report",
		"persistent HTTP 500 errors to the Fedora Infrastructure team.",
		"You can retrieve the information about available branches by querying ",
		"the following request.",
		"Please ensure that the database directory has been configured properly",
		"and the scheduled downloads have been functioning correctly.",
	}
	for _, item := range subslist {
		if !strings.Contains(record.Body.String(), item) {
			t.Errorf("Absent '%s'", item)
		}
	}

	if !strings.Contains(record.Header().Get("content-type"), "text/html") {
		t.Errorf("Received %s, Expected %s", record.Header().Get("content-type"), "text/html")
	}

	if record.Code != http.StatusOK {
		t.Errorf("Received %d, Expected %d", record.Code, http.StatusOK)
	}
}

func TestHome_Init_Success(t *testing.T) {
	Path_Init(t, "")

	router := option.Navigate()
	rqster := httptest.NewRequest("GET", "/", nil)
	record := httptest.NewRecorder()
	router.ServeHTTP(record, rqster)

	subslist := []string{
		"You can retrieve the information about a specific package on",
		"a specific branch by querying its package name.",
		"You can retrieve the information about a specific package on",
		"a specific branch by querying its source name.",
		"You can retrieve the list of files present in a specific ",
		"package on a specific branch by querying its package name.",
		"You can retrieve the changelog of a specific package on a ",
		"specific branch by querying its package name.",
		"You can retrieve the list of packages requiring a specific ",
		"package on a specific branch by querying its package name.",
		"You can retrieve the list of packages providing a specific ",
		"package on a specific branch by querying its package name.",
		"You can retrieve the list of packages obsoleting a specific ",
		"package on a specific branch by querying its package name.",
		"You can retrieve the list of packages conflicting a specific ",
		"package on a specific branch by querying its package name.",
		"You can retrieve the list of packages enhancing a specific ",
		"package on a specific branch by querying its package name.",
		"You can retrieve the list of packages recommending a specific",
		"package on a specific branch by querying its package name.",
		"You can retrieve the list of packages suggesting a specific ",
		"package on a specific branch by querying its package name.",
		"You can retrieve the list of packages providing a specific ",
		"package on a specific branch by querying its package name.",
	}

	for _, item := range subslist {
		if !strings.Contains(record.Body.String(), item) {
			t.Errorf("Absent '%s'", item)
		}
	}

	if !strings.Contains(record.Header().Get("content-type"), "text/html") {
		t.Errorf("Received %s, Expected %s", record.Header().Get("content-type"), "text/html")
	}

	if record.Code != http.StatusOK {
		t.Errorf("Received %d, Expected %d", record.Code, http.StatusOK)
	}
}

func TestHome_UnInit_Failure_FaultyTemplate_C500(t *testing.T) {
	Path_UnInit(t, "/var/tmp")

	original := routes.HomeHTML
	routes.HomeHTML = []byte(`{{ if .Name }}Hello{{ end >>`)
	defer func() { routes.HomeHTML = original }()

	router := option.Navigate()
	rqster := httptest.NewRequest("GET", "/", nil)
	record := httptest.NewRecorder()
	router.ServeHTTP(record, rqster)

	if !strings.Contains(record.Header().Get("content-type"), "text/plain") {
		t.Errorf("Received %s, Expected %s", record.Header().Get("content-type"), "text/plain")
	}

	if record.Code != http.StatusInternalServerError {
		t.Errorf("Received %d, Expected %d", record.Code, http.StatusInternalServerError)
	}
}

func TestHome_UnInit_Failure_ReadBranches_C500(t *testing.T) {
	Path_UnInit(t, "/var/tmp")

	original := lookup.ReadBranches
	lookup.ReadBranches = func() ([]string, error) {
		return []string{}, errors.New("ReadBranches failed")
	}
	defer func() { lookup.ReadBranches = original }()

	router := option.Navigate()
	rqster := httptest.NewRequest("GET", "/", nil)
	record := httptest.NewRecorder()
	router.ServeHTTP(record, rqster)

	if !strings.Contains(record.Header().Get("content-type"), "text/plain") {
		t.Errorf("Received %s, Expected %s", record.Header().Get("content-type"), "text/plain")
	}

	if record.Code != http.StatusInternalServerError {
		t.Errorf("Received %d, Expected %d", record.Code, http.StatusInternalServerError)
	}
}

func TestHome_UnInit_Failure_LastModified(t *testing.T) {
	Path_UnInit(t, "/var/tmp")

	original := lookup.ReadBranches
	lookup.ReadBranches = func() ([]string, error) {
		return []string{"koji"}, nil
	}
	defer func() { lookup.ReadBranches = original }()

	router := option.Navigate()
	rqster := httptest.NewRequest("GET", "/", nil)
	record := httptest.NewRecorder()
	router.ServeHTTP(record, rqster)

	subslist := []string{
		"MetaSource is a performant source for RPM repositories metadata which ",
		"has an access to the metadata of the different Fedora Linux package ",
		"repositories and will serve you the most recent information available.",
		"It will parse through the \"updates-testing\" repository before moving",
		"onto the likes of \"updates\" and \"releases\" repository if no ",
		"information is found in the previous repository.",
		"Utilize the fast lookup interface to acquaint yourself with the API ",
		"endpoints and expected outputs. Press ENTER after typing the name to ",
		"execute a lookup in a new window. If you query for a non-existent ",
		"branch - it will return an HTTP 400 error. If you query for a ",
		"non-existent package - it will return an HTTP 404 error. Please report",
		"persistent HTTP 500 errors to the Fedora Infrastructure team.",
		"You can retrieve the information about available branches by querying ",
		"the following request.",
		"Please ensure that the database directory has been configured properly",
		"and the scheduled downloads have been functioning correctly.",
	}
	for _, item := range subslist {
		if !strings.Contains(record.Body.String(), item) {
			t.Errorf("Absent '%s'", item)
		}
	}

	if !strings.Contains(record.Header().Get("content-type"), "text/html") {
		t.Errorf("Received %s, Expected %s", record.Header().Get("content-type"), "text/html")
	}

	if record.Code != http.StatusOK {
		t.Errorf("Received %d, Expected %d", record.Code, http.StatusOK)
	}
}
