package routes

import (
	"encoding/json"
	"fmt"
	"github.com/go-chi/chi/v5"
	"metasource/metasource/lookup"
	"metasource/metasource/models"
	"net/http"
)

func RetrieveSrce(w http.ResponseWriter, r *http.Request) {
	var name, vers, repo string
	var rslt models.UnitPrimary
	var pack models.PackUnit
	var data models.ExtnUnit
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

	rslt = models.UnitPrimary{
		Repo:          repo,
		Arch:          pack.Arch.String,
		Epoch:         pack.Epoch.String,
		Version:       pack.Version.String,
		Release:       pack.Release.String,
		Summary:       pack.Summary.String,
		Description:   pack.Desc.String,
		Basename:      pack.Name.String,
		URL:           pack.Link.String,
		CoPackages:    coop,
		SizePackage:   pack.SizePackage.String,
		SizeInstalled: pack.SizeInstalled.String,
	}
	if rslt.Repo == "" {
		rslt.Repo = "release"
	}

	rslt.Supplements = []models.UnitBase{}
	for _, item := range data.Supplements {
		utbs := models.UnitBase{
			Version: item.Version.String,
			Epoch:   item.Epoch.String,
			Release: item.Release.String,
			Name:    item.Name.String,
			Flags:   item.Flags.String,
		}
		rslt.Supplements = append(rslt.Supplements, utbs)
	}

	rslt.Recommends = []models.UnitBase{}
	for _, item := range data.Recommends {
		utbs := models.UnitBase{
			Version: item.Version.String,
			Epoch:   item.Epoch.String,
			Release: item.Release.String,
			Name:    item.Name.String,
			Flags:   item.Flags.String,
		}
		rslt.Recommends = append(rslt.Recommends, utbs)
	}

	rslt.Conflicts = []models.UnitBase{}
	for _, item := range data.Conflicts {
		utbs := models.UnitBase{
			Version: item.Version.String,
			Epoch:   item.Epoch.String,
			Release: item.Release.String,
			Name:    item.Name.String,
			Flags:   item.Flags.String,
		}
		rslt.Conflicts = append(rslt.Conflicts, utbs)
	}

	rslt.Obsoletes = []models.UnitBase{}
	for _, item := range data.Obsoletes {
		utbs := models.UnitBase{
			Version: item.Version.String,
			Epoch:   item.Epoch.String,
			Release: item.Release.String,
			Name:    item.Name.String,
			Flags:   item.Flags.String,
		}
		rslt.Obsoletes = append(rslt.Obsoletes, utbs)
	}

	rslt.Provides = []models.UnitBase{}
	for _, item := range data.Provides {
		utbs := models.UnitBase{
			Version: item.Version.String,
			Epoch:   item.Epoch.String,
			Release: item.Release.String,
			Name:    item.Name.String,
			Flags:   item.Flags.String,
		}
		rslt.Provides = append(rslt.Provides, utbs)
	}

	rslt.Requires = []models.UnitBase{}
	for _, item := range data.Requires {
		utbs := models.UnitBase{
			Version: item.Version.String,
			Epoch:   item.Epoch.String,
			Release: item.Release.String,
			Name:    item.Name.String,
			Flags:   item.Flags.String,
		}
		rslt.Requires = append(rslt.Requires, utbs)
	}

	rslt.Enhances = []models.UnitBase{}
	for _, item := range data.Enhances {
		utbs := models.UnitBase{
			Version: item.Version.String,
			Epoch:   item.Epoch.String,
			Release: item.Release.String,
			Name:    item.Name.String,
			Flags:   item.Flags.String,
		}
		rslt.Enhances = append(rslt.Enhances, utbs)
	}

	rslt.Suggests = []models.UnitBase{}
	for _, item := range data.Suggests {
		utbs := models.UnitBase{
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
