package test

import (
	"metasource/metasource/config"
	"metasource/metasource/option"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestStat_Init_Success(t *testing.T) {
	Path_UnInit(t, "/var/tmp")

	router := option.Navigate()
	rqster := httptest.NewRequest("GET", "/assets/bs.js", nil)
	record := httptest.NewRecorder()
	router.ServeHTTP(record, rqster)

	if !strings.Contains(record.Header().Get("content-type"), "text/javascript") {
		t.Errorf("Received %s, Expected %s", record.Header().Get("content-type"), "text/javascript")
	}

	if record.Code != http.StatusOK {
		t.Errorf("Received %d, Expected %d", record.Code, http.StatusOK)
	}
}

func TestStat_Init_Failure_C404(t *testing.T) {
	Path_UnInit(t, "/var/tmp")

	router := option.Navigate()
	rqster := httptest.NewRequest("GET", "/static/bs.js", nil)
	record := httptest.NewRecorder()
	router.ServeHTTP(record, rqster)

	if !strings.Contains(record.Header().Get("content-type"), "text/plain") {
		t.Errorf("Received %s, Expected %s", record.Header().Get("content-type"), "text/plain")
	}

	if record.Code != http.StatusNotFound {
		t.Errorf("Received %d, Expected %d", record.Code, http.StatusNotFound)
	}
}

func TestStat_Init_Failure_C500(t *testing.T) {
	Path_UnInit(t, "/var/tmp")

	original := config.ASSETSDB
	config.ASSETSDB = "/usr"
	defer func() { config.ASSETSDB = original }()

	router := option.Navigate()
	rqster := httptest.NewRequest("GET", "/assets/bs.js", nil)
	record := httptest.NewRecorder()
	router.ServeHTTP(record, rqster)

	if !strings.Contains(record.Header().Get("content-type"), "text/plain") {
		t.Errorf("Received %s, Expected %s", record.Header().Get("content-type"), "text/plain")
	}

	if record.Code != http.StatusInternalServerError {
		t.Errorf("Received %d, Expected %d", record.Code, http.StatusInternalServerError)
	}
}
