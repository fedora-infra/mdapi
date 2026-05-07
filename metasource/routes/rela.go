package routes

import (
	"encoding/json"
	"fmt"
	"github.com/go-chi/chi/v5"
	"metasource/metasource/lookup"
	"metasource/metasource/models"
	"net/http"
)

func RetrieveRelation(w http.ResponseWriter, r *http.Request) {
	var name, vers, repo, rela string
	var rslt []models.UnitPrimary
	var pkit models.UnitPrimary
	var pack, item models.PackUnit
	var data []models.PackUnit
	var extn models.ExtnUnit
	var dpit models.DepsUnit
	var coop []string
	var expt error

	name = chi.URLParam(r, "name")
	vers = chi.URLParam(r, "vers")
	rela = chi.URLParam(r, "rela")

	if name == "" || vers == "" || rela == "" {
		http.Error(w, fmt.Sprintf("%d: %s", http.StatusBadRequest, http.StatusText(http.StatusBadRequest)), http.StatusBadRequest)
		return
	}

	switch rela {
	case "supplements", "recommends", "conflicts", "obsoletes", "provides", "requires", "enhances", "suggests":
	default:
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

	data, expt = lookup.ReadRelation(&vers, &pack, &repo, &rela)
	if expt != nil {
		http.Error(w, fmt.Sprintf("%d: %s", http.StatusBadRequest, http.StatusText(http.StatusBadRequest)), http.StatusBadRequest)
		return
	}

	rslt = []models.UnitPrimary{}

	for _, item = range data {
		extn, expt = lookup.ReadExtn(&vers, &item, &repo)
		if expt != nil {
			http.Error(w, fmt.Sprintf("%d: %s", http.StatusBadRequest, http.StatusText(http.StatusBadRequest)), http.StatusBadRequest)
			return
		}

		coop, expt = lookup.ReadCoop(&vers, &item, &repo)
		if expt != nil {
			http.Error(w, fmt.Sprintf("%d: %s", http.StatusBadRequest, http.StatusText(http.StatusBadRequest)), http.StatusBadRequest)
			return
		}

		pkit = models.UnitPrimary{
			Repo:          repo,
			Arch:          item.Arch.String,
			Epoch:         item.Epoch.String,
			Version:       item.Version.String,
			Release:       item.Release.String,
			Summary:       item.Summary.String,
			Description:   item.Desc.String,
			Basename:      item.Name.String,
			URL:           item.Link.String,
			CoPackages:    coop,
			SizePackage:   item.SizePackage.String,
			SizeInstalled: item.SizeInstalled.String,
		}
		if pkit.Repo == "" {
			pkit.Repo = "release"
		}

		pkit.Supplements = []models.UnitBase{}
		for _, dpit = range extn.Supplements {
			utbs := models.UnitBase{
				Version: dpit.Version.String,
				Epoch:   dpit.Epoch.String,
				Release: dpit.Release.String,
				Name:    dpit.Name.String,
				Flags:   dpit.Flags.String,
			}
			pkit.Supplements = append(pkit.Supplements, utbs)
		}

		pkit.Recommends = []models.UnitBase{}
		for _, dpit = range extn.Recommends {
			utbs := models.UnitBase{
				Version: dpit.Version.String,
				Epoch:   dpit.Epoch.String,
				Release: dpit.Release.String,
				Name:    dpit.Name.String,
				Flags:   dpit.Flags.String,
			}
			pkit.Recommends = append(pkit.Recommends, utbs)
		}

		pkit.Conflicts = []models.UnitBase{}
		for _, dpit = range extn.Conflicts {
			utbs := models.UnitBase{
				Version: dpit.Version.String,
				Epoch:   dpit.Epoch.String,
				Release: dpit.Release.String,
				Name:    dpit.Name.String,
				Flags:   dpit.Flags.String,
			}
			pkit.Conflicts = append(pkit.Conflicts, utbs)
		}

		pkit.Obsoletes = []models.UnitBase{}
		for _, dpit = range extn.Obsoletes {
			utbs := models.UnitBase{
				Version: dpit.Version.String,
				Epoch:   dpit.Epoch.String,
				Release: dpit.Release.String,
				Name:    dpit.Name.String,
				Flags:   dpit.Flags.String,
			}
			pkit.Obsoletes = append(pkit.Obsoletes, utbs)
		}

		pkit.Provides = []models.UnitBase{}
		for _, dpit = range extn.Provides {
			utbs := models.UnitBase{
				Version: dpit.Version.String,
				Epoch:   dpit.Epoch.String,
				Release: dpit.Release.String,
				Name:    dpit.Name.String,
				Flags:   dpit.Flags.String,
			}
			pkit.Provides = append(pkit.Provides, utbs)
		}

		pkit.Requires = []models.UnitBase{}
		for _, dpit = range extn.Requires {
			utbs := models.UnitBase{
				Version: dpit.Version.String,
				Epoch:   dpit.Epoch.String,
				Release: dpit.Release.String,
				Name:    dpit.Name.String,
				Flags:   dpit.Flags.String,
			}
			pkit.Requires = append(pkit.Requires, utbs)
		}

		pkit.Enhances = []models.UnitBase{}
		for _, dpit = range extn.Enhances {
			utbs := models.UnitBase{
				Version: dpit.Version.String,
				Epoch:   dpit.Epoch.String,
				Release: dpit.Release.String,
				Name:    dpit.Name.String,
				Flags:   dpit.Flags.String,
			}
			pkit.Enhances = append(pkit.Enhances, utbs)
		}

		pkit.Suggests = []models.UnitBase{}
		for _, dpit = range extn.Suggests {
			utbs := models.UnitBase{
				Version: dpit.Version.String,
				Epoch:   dpit.Epoch.String,
				Release: dpit.Release.String,
				Name:    dpit.Name.String,
				Flags:   dpit.Flags.String,
			}
			pkit.Suggests = append(pkit.Suggests, utbs)
		}

		rslt = append(rslt, pkit)
	}

	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	_ = json.NewEncoder(w).Encode(rslt)
}
