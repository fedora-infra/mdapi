package routes

import (
	"encoding/json"
	"fmt"
	"github.com/go-chi/chi/v5"
	"metasource/metasource/lookup"
	"metasource/metasource/models/dict"
	"metasource/metasource/models/home"
	"net/http"
)

func RetrieveFileList(w http.ResponseWriter, r *http.Request) {
	var name, vers, repo string
	var rslt dict.UnitFileList
	var data home.FilelistRslt
	var pack home.PackUnit
	var expt error

	name = chi.URLParam(r, "name")
	vers = chi.URLParam(r, "vers")

	if name == "" || vers == "" {
		http.Error(w, fmt.Sprintf("%d: %s", http.StatusBadRequest, http.StatusText(http.StatusBadRequest)), http.StatusBadRequest)
		return
	}

	pack, repo, expt = lookup.ReadPrmy(&vers, &name)
	if expt != nil {
		if expt.Error() == "no result found" {
			http.Error(w, fmt.Sprintf("%d: %s", http.StatusNotFound, http.StatusText(http.StatusNotFound)), http.StatusNotFound)
			return
		}
		http.Error(w, fmt.Sprintf("%d: %s", http.StatusBadRequest, http.StatusText(http.StatusBadRequest)), http.StatusBadRequest)
		return
	}

	data, expt = lookup.ReadFile(&vers, &pack, &repo)
	if expt != nil {
		http.Error(w, fmt.Sprintf("%d: %s", http.StatusBadRequest, http.StatusText(http.StatusBadRequest)), http.StatusBadRequest)
		return
	}

	rslt = dict.UnitFileList{}
	rslt.Repo = repo
	if rslt.Repo == "" {
		rslt.Repo = "release"
	}

	for _, item := range data.List {
		var unit dict.File
		unit.FileTypes = item.Type.String
		unit.DirName = item.Directory.String
		unit.FileNames = item.Name.String
		rslt.Files = append(rslt.Files, unit)
	}

	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	_ = json.NewEncoder(w).Encode(rslt)
}
