package routes

import (
	"encoding/json"
	"fmt"
	"metasource/metasource/lookup"
	"net/http"
)

func RetrieveBranches(w http.ResponseWriter, r *http.Request) {
	var rslt []string
	var expt error

	rslt, expt = lookup.ReadBranches()
	if expt != nil {
		http.Error(w, fmt.Sprintf("%d: %s", http.StatusInternalServerError, http.StatusText(http.StatusInternalServerError)), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	_ = json.NewEncoder(w).Encode(rslt)
}
