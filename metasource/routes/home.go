package routes

import (
	_ "embed"
	"fmt"
	"github.com/dustin/go-humanize"
	"html/template"
	"metasource/metasource/config"
	"metasource/metasource/lookup"
	"metasource/metasource/models/page"
	"net/http"
	"os"
	"strings"
)

//go:embed shapes/home.html
var HomeHTML []byte

var LastModified = func(list []string) map[string]page.Vary {
	var info_primary, info_filelists, info_changelog os.FileInfo
	datelist := map[string]page.Vary{}

	for _, brch := range list {
		for _, repo := range []string{"updates-testing", "updates", "testing", ""} {
			var expt_primary, expt_filelists, expt_changelog error
			var name_primary, name_filelists, name_changelog string
			switch repo {
			case "updates-testing", "updates", "testing":
				name_primary = fmt.Sprintf("metasource-%s-%s-primary.sqlite", brch, repo)
				name_filelists = fmt.Sprintf("metasource-%s-%s-filelists.sqlite", brch, repo)
				name_changelog = fmt.Sprintf("metasource-%s-%s-other.sqlite", brch, repo)
			default:
				name_primary = fmt.Sprintf("metasource-%s-primary.sqlite", brch)
				name_filelists = fmt.Sprintf("metasource-%s-filelists.sqlite", brch)
				name_changelog = fmt.Sprintf("metasource-%s-other.sqlite", brch)
			}
			location_primary := fmt.Sprintf("%s/%s", config.DBFOLDER, name_primary)
			location_filelists := fmt.Sprintf("%s/%s", config.DBFOLDER, name_filelists)
			location_changelog := fmt.Sprintf("%s/%s", config.DBFOLDER, name_changelog)
			if info_primary == nil {
				info_primary, expt_primary = os.Stat(location_primary)
			}
			if info_filelists == nil {
				info_filelists, expt_filelists = os.Stat(location_filelists)
			}
			if info_changelog == nil {
				info_changelog, expt_changelog = os.Stat(location_changelog)
			}
			if expt_primary != nil || expt_filelists != nil || expt_changelog != nil {
				continue
			}
		}
		if info_primary != nil && info_filelists != nil && info_changelog != nil {
			datelist[brch] = page.Vary{
				Primary: page.Date{
					When: info_primary.ModTime().Format("2006-01-02 15:04:05 MST"),
					Past: humanize.Time(info_primary.ModTime()),
				},
				Changelog: page.Date{
					When: info_changelog.ModTime().Format("2006-01-02 15:04:05 MST"),
					Past: humanize.Time(info_changelog.ModTime()),
				},
				Filelists: page.Date{
					When: info_filelists.ModTime().Format("2006-01-02 15:04:05 MST"),
					Past: humanize.Time(info_filelists.ModTime()),
				},
				Safe: strings.Replace(brch, ".", "_", -1),
			}
		}
	}
	return datelist
}

func RetrieveHome(w http.ResponseWriter, r *http.Request) {
	var expt error

	tmpl, expt := template.New("home").Parse(string(HomeHTML))
	if expt != nil {
		http.Error(w, fmt.Sprintf("%d: %s", http.StatusInternalServerError, http.StatusText(http.StatusInternalServerError)), http.StatusInternalServerError)
		return
	}

	list, expt := lookup.ReadBranches()
	if expt != nil {
		http.Error(w, fmt.Sprintf("%d: %s", http.StatusInternalServerError, http.StatusText(http.StatusInternalServerError)), http.StatusInternalServerError)
		return
	}

	park := []page.Card{
		{
			Iden: "package",
			Head: "Package",
			Desc: "You can retrieve the information about a specific package on a specific branch by querying its package name.",
			Path: "pkg",
		},
		{
			Iden: "source",
			Head: "Source",
			Desc: "You can retrieve the information about a specific package on a specific branch by querying its source name.",
			Path: "srcpkg",
		},
		{
			Iden: "filelist",
			Head: "Filelist",
			Desc: "You can retrieve the list of files present in a specific package on a specific branch by querying its package name.",
			Path: "files",
		},
		{
			Iden: "changelog",
			Head: "Changelog",
			Desc: "You can retrieve the changelog of a specific package on a specific branch by querying its package name.",
			Path: "changelog",
		},
		{
			Iden: "requires",
			Head: "Requires",
			Desc: "You can retrieve the list of packages requiring a specific package on a specific branch by querying its package name.",
			Path: "requires",
		},
		{
			Iden: "provides",
			Head: "Provides",
			Desc: "You can retrieve the list of packages providing a specific package on a specific branch by querying its package name.",
			Path: "provides",
		},
		{
			Iden: "obsoletes",
			Head: "Obsoletes",
			Desc: "You can retrieve the list of packages obsoleting a specific package on a specific branch by querying its package name.",
			Path: "obsoletes",
		},
		{
			Iden: "conflicts",
			Head: "Conflicts",
			Desc: "You can retrieve the list of packages conflicting a specific package on a specific branch by querying its package name.",
			Path: "conflicts",
		},
		{
			Iden: "enhances",
			Head: "Enhances",
			Desc: "You can retrieve the list of packages enhancing a specific package on a specific branch by querying its package name.",
			Path: "enhances",
		},
		{
			Iden: "recommends",
			Head: "Recommends",
			Desc: "You can retrieve the list of packages recommending a specific package on a specific branch by querying its package name.",
			Path: "recommends",
		},
		{
			Iden: "suggests",
			Head: "Suggests",
			Desc: "You can retrieve the list of packages suggesting a specific package on a specific branch by querying its package name.",
			Path: "suggests",
		},
		{
			Iden: "supplements",
			Head: "Supplements",
			Desc: "You can retrieve the list of packages providing a specific package on a specific branch by querying its package name.",
			Path: "supplements",
		},
	}

	data := page.Page{
		Name: "MetaSource",
		Vers: "v0.1.0",
		Host: "metasource.gridhead.net",
		Conn: "https",
		Dict: LastModified(list),
		Park: park,
	}

	w.Header().Set("Content-Type", "text/html")
	_ = tmpl.Execute(w, data)
}
