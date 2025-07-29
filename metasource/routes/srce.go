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

func RetrieveSrce(w http.ResponseWriter, r *http.Request) {
	var name, vers, repo string
	var rslt dict.UnitPrimary
	var pack home.PackUnit
	var data home.ExtnUnit
	var coop []string
	var expt error

	name = chi.URLParam(r, "name")
	vers = chi.URLParam(r, "vers")

	if name == "" || vers == "" {
		http.Error(w, fmt.Sprintf("%d: %s", http.StatusBadRequest, http.StatusText(http.StatusBadRequest)), http.StatusBadRequest)
		return
	}

	pack, repo, expt = lookup.ReadSrce(&vers, &name)
	if expt != nil {
		if expt.Error() == "no result found" {
			http.Error(w, fmt.Sprintf("%d: %s", http.StatusNotFound, http.StatusText(http.StatusNotFound)), http.StatusNotFound)
			return
		}
		http.Error(w, fmt.Sprintf("%d: %s", http.StatusBadRequest, http.StatusText(http.StatusBadRequest)), http.StatusBadRequest)
		return
	}

	data, expt = lookup.ReadExtn(&vers, &pack, &repo)
	if expt != nil {
		http.Error(w, fmt.Sprintf("%d: %s", http.StatusBadRequest, http.StatusText(http.StatusBadRequest)), http.StatusBadRequest)
		return
	}

	coop, expt = lookup.ReadCoop(&vers, &pack, &repo)
	if expt != nil {
		http.Error(w, fmt.Sprintf("%d: %s", http.StatusBadRequest, http.StatusText(http.StatusBadRequest)), http.StatusBadRequest)
		return
	}

	rslt = dict.UnitPrimary{
		Repo:        repo,
		Arch:        pack.Arch.String,
		Epoch:       pack.Epoch.String,
		Version:     pack.Version.String,
		Release:     pack.Release.String,
		Summary:     pack.Summary.String,
		Description: pack.Desc.String,
		Basename:    pack.Name.String,
		URL:         pack.Link.String,
		CoPackages:  coop,
	}
	if rslt.Repo == "" {
		rslt.Repo = "release"
	}

	rslt.Supplements = []dict.UnitBase{}
	for _, item := range data.Supplements {
		utbs := dict.UnitBase{
			Version: item.Version.String,
			Epoch:   item.Epoch.String,
			Release: item.Release.String,
			Name:    item.Name.String,
			Flags:   item.Flags.String,
		}
		rslt.Supplements = append(rslt.Supplements, utbs)
	}

	rslt.Recommends = []dict.UnitBase{}
	for _, item := range data.Recommends {
		utbs := dict.UnitBase{
			Version: item.Version.String,
			Epoch:   item.Epoch.String,
			Release: item.Release.String,
			Name:    item.Name.String,
			Flags:   item.Flags.String,
		}
		rslt.Recommends = append(rslt.Recommends, utbs)
	}

	rslt.Conflicts = []dict.UnitBase{}
	for _, item := range data.Conflicts {
		utbs := dict.UnitBase{
			Version: item.Version.String,
			Epoch:   item.Epoch.String,
			Release: item.Release.String,
			Name:    item.Name.String,
			Flags:   item.Flags.String,
		}
		rslt.Conflicts = append(rslt.Conflicts, utbs)
	}

	rslt.Obsoletes = []dict.UnitBase{}
	for _, item := range data.Obsoletes {
		utbs := dict.UnitBase{
			Version: item.Version.String,
			Epoch:   item.Epoch.String,
			Release: item.Release.String,
			Name:    item.Name.String,
			Flags:   item.Flags.String,
		}
		rslt.Obsoletes = append(rslt.Obsoletes, utbs)
	}

	rslt.Provides = []dict.UnitBase{}
	for _, item := range data.Provides {
		utbs := dict.UnitBase{
			Version: item.Version.String,
			Epoch:   item.Epoch.String,
			Release: item.Release.String,
			Name:    item.Name.String,
			Flags:   item.Flags.String,
		}
		rslt.Provides = append(rslt.Provides, utbs)
	}

	rslt.Requires = []dict.UnitBase{}
	for _, item := range data.Requires {
		utbs := dict.UnitBase{
			Version: item.Version.String,
			Epoch:   item.Epoch.String,
			Release: item.Release.String,
			Name:    item.Name.String,
			Flags:   item.Flags.String,
		}
		rslt.Requires = append(rslt.Requires, utbs)
	}

	rslt.Enhances = []dict.UnitBase{}
	for _, item := range data.Enhances {
		utbs := dict.UnitBase{
			Version: item.Version.String,
			Epoch:   item.Epoch.String,
			Release: item.Release.String,
			Name:    item.Name.String,
			Flags:   item.Flags.String,
		}
		rslt.Enhances = append(rslt.Enhances, utbs)
	}

	rslt.Suggests = []dict.UnitBase{}
	for _, item := range data.Suggests {
		utbs := dict.UnitBase{
			Version: item.Version.String,
			Epoch:   item.Epoch.String,
			Release: item.Release.String,
			Name:    item.Name.String,
			Flags:   item.Flags.String,
		}
		rslt.Suggests = append(rslt.Suggests, utbs)
	}

	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	_ = json.NewEncoder(w).Encode(rslt)
}
